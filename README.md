# Auditing AI Data Analysts: A Three-Tier Evaluation of Data Agents

*Can you trust an AI agent to analyze your data? I tested three tiers of data agents on the same real-world e-commerce dataset — and audited every number they produced against independently computed ground truth.*

**TL;DR: Every agent executed code correctly. Almost none of them agreed with each other.** The failures were not arithmetic — they were silent, undeclared choices of *definitions*: which reference date, mean vs. median thresholds, whether boundaries include equality. The better the agent, the more professional its mistakes looked.

## Setup

| | Tier | Agents tested | Cost |
|---|------|--------------|------|
| 1 | General-purpose agents | Kimi (Moonshot), Codex (OpenAI / GPT-5.5) | Free tier |
| 2 | Cloud data-analysis specialist | Julius AI | Free credits |
| 3 | Local private deployment | DB-GPT + Ollama (qwen3:4b → qwen2.5:3b) | Free, fully offline |

**Dataset:** ~23K e-commerce orders, 3,399 users, 2015–2020 (transaction time, user id, order id, amount). Raw data not included in this repo — see [`data/README.md`](data/README.md).

**Method:** identical questions to each agent (row counts, monthly revenue, RFM segmentation, churn definition, per-user recency, data-quality diagnosis), every answer re-computed independently with pandas / lifetimes ([`ground_truth/`](ground_truth/)).

## Scoreboard (selected)

| Question | Kimi | Codex | Ground truth |
|----------|------|-------|--------------|
| Row count | 23,287 ✗ (off by one) | 23,288 ✓ | 23,288 — file lacks trailing newline; newline-counting undercounts |
| Distinct users / time range / top revenue month | ✓ | ✓ | agree |
| RFM: "high-value" segment size | **948** | **653** | *both correct* — Kimi used median + ≥, Codex used mean; one undeclared choice moved ~300 users |
| Churn threshold | 730 days (inferred business context from distribution) | 585 days (= mean R) | no ground truth — this is a business decision, not a computation |
| Per-user recency (R) | all values +1 day | 87% exact | different reference dates (2020-04-26 vs 2020-04-25 21:34), both *declared*, still incompatible |
| Data-quality scan | found 0-amount orders, duplicate order id | + trailing spaces in all 23,288 order ids, 68 order-id/date mismatches | verified ✓ |

Full details in [`findings.md`](findings.md).

## Five findings

1. **The dangerous failures are not wrong calculations — they are undeclared definitions.** Two agents both "correctly" ran RFM and produced segment sizes differing by 2×, because mean-vs-median and `>` vs `≥` were silently chosen.
2. **Transparency is not compatibility.** On the recency task both agents *declared* their reference dates — and still produced systematically incompatible results. Only a human can fix the definition.
3. **Smarter agents make more convincing mistakes.** Kimi inferred a plausible business context ("low-frequency durable goods") from the distribution alone — insightful *and* unverifiable. True and false insights look identical until you recompute.
4. **The auditor can fail too.** While verifying a "trailing spaces" claim, my own verification pipeline (pandas type inference) silently stripped the spaces and nearly convicted a correct agent of hallucination. Verification methods need verification.
5. **Local deployment's bottleneck is the model, not the framework.** DB-GPT deployed fine; a 4B reasoning model burned all tokens on thinking and returned empty answers, and a 3B model needed 20+ steps (syntax error → empty output → shell fallback) for a question cloud agents answered in one shot. Full log: [`03_local_deployment/`](03_local_deployment/).

## Why this matters

Data agents are becoming the default interface to company data. This experiment suggests the near-term risk is not "the AI computes wrong numbers" — it is **plausible, reproducible, internally consistent answers built on definitions nobody signed off on**. The human role shifts from writing queries to *defining metrics and auditing conclusions* — which is exactly the part that cannot be delegated.

## Repo structure

```
01_general_agents/     Kimi vs Codex: six-question head-to-head (screenshots + notes)
02_cloud_specialist/   Julius AI: data-quality deep-dive audit (screenshots + notes)
03_local_deployment/   DB-GPT + Ollama deployment log and failure analysis
ground_truth/          pandas / lifetimes scripts used to audit every claim
data/                  dataset description (raw data not distributed)
```

## Background

Done during a data-analysis internship program (2026). The companion repo [user-value-analytics](../user-value-analytics) contains the underlying RFM / cohort-retention / LTV analyses I built by hand — which is what made the auditing possible.
