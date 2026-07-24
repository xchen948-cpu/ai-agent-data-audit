# Auditing AI Agents as Data Analysts

*Two general-purpose AI agents, one real e-commerce dataset, six identical questions,
and every answer re-computed by hand to see who was right.*

**TL;DR: both agents executed code correctly, and they still disagreed.** The
disagreements were not arithmetic errors, they were silent, undeclared choices of
*definition*: which reference date, mean vs. median thresholds, whether a boundary
includes equality. One such choice moved ~300 users between customer segments.

## Setup

| | |
|---|---|
| **Agents** | Kimi (Moonshot AI) · Codex (OpenAI, GPT-5.5) |
| **Dataset** | ~23K e-commerce orders, 3,399 users, 2015–2020 (transaction time, user id, order id, amount) |
| **Method** | identical questions to both agents; every answer independently re-computed with pandas / lifetimes |
| **Ground truth** | [`ground_truth/`](ground_truth/) — runnable scripts |

Both tools genuinely write and execute code on the uploaded file (agent behaviour),
rather than guessing from a preview, which is what makes the disagreements interesting.

## Scoreboard

| Question | Kimi | Codex | Verified answer |
|----------|------|-------|-----------------|
| Row count | 23,287 ✗ | 23,288 ✓ | **23,288** — the file has no trailing newline, so newline-counting undercounts by one |
| Distinct users | 3,399 ✓ | 3,399 ✓ | 3,399 |
| Time range | ✓ | ✓ | 2015-02-12 15:04 → 2020-04-25 21:34 |
| Highest-revenue month | 2019-12, 10,030,508 ✓ | same ✓ | exact match |
| RFM 8-segment sizes | high-value **948** | high-value **653** | *both correct* — different undeclared thresholds (median + ≥ vs mean) |
| Churn threshold | 730 days, inferred "low-frequency / high-ticket retail" from the distribution | 585 days (= mean recency) | no ground truth — this is a business decision |
| Per-user recency (R) | every value +1 day | 87% exact | different reference dates (2020-04-26 vs 2020-04-25 21:34), both declared |
| Data-quality scan | 1,174 zero-amount orders, duplicated order id | + trailing spaces on all 23,288 order ids, 68 order-id/date mismatches | all verified ✓ |

Details and root-cause analysis for each row: [`findings.md`](findings.md).

## Four takeaways

1. **The dangerous failures are undeclared definitions, not wrong arithmetic.**
   Both agents ran "RFM" correctly and produced high-value segments differing by
   ~45%, because mean-vs-median and `>` vs `≥` were chosen silently.
   Reproduce both results: [`rfm_threshold_reproduction.py`](ground_truth/rfm_threshold_reproduction.py).

2. **Transparency ≠ compatibility.** On the recency task both agents *declared*
   their reference dates and were still systematically one day apart. Declaring
   assumptions is the agent's job; unifying them is the human's.

3. **Smarter agents make more convincing mistakes.** Kimi inferred a plausible
   business context ("low-frequency, high-ticket retail") purely from the
   distribution — insightful, fluent, and unverifiable. True and false insights
   read identically.

4. **The auditor can fail too.** Verifying the "trailing spaces" claim, my own
   pandas pipeline silently cast order ids to integers — stripping the spaces —
   and nearly convicted a correct agent of hallucinating. Re-reading the file as
   raw strings confirmed the agent was right. Verification methods need verification.

## Why it matters

AI agents are becoming the default interface to company data. This experiment
suggests the near-term risk is not "the AI computes the wrong number" — it is
**plausible, internally consistent, reproducible answers built on definitions
nobody signed off on**. The human role shifts from writing queries to *defining
metrics and auditing conclusions*.

## Repo structure

```
ground_truth/    pandas / lifetimes scripts that verified every claim
screenshots/     agent conversation screenshots per question
data/            dataset description (raw data not distributed)
findings.md      per-question analysis with root causes
```

## Reproduce

```bash
pip install pandas lifetimes
python ground_truth/audit_baseline.py path/to/orders.csv
python ground_truth/rfm_threshold_reproduction.py path/to/orders.csv
```

---

Built during a data-analysis internship (2026). The underlying RFM / cohort-retention /
LTV analyses I implemented by hand — which is what made auditing the agents possible —
live in a companion repo.
