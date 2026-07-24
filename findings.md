# Detailed Findings

All numbers below were verified by independent recomputation with pandas / lifetimes
(scripts in [`ground_truth/`](ground_truth/)). Dataset: ~23K orders, 3,399 users, 2015–2020.

---

## 1. The row-count trap: the human baseline was the thing that broke

**Question:** "How many rows does this file have?"

| Source | Answer |
|--------|--------|
| Kimi | 23,288 rows in the file; 23,287 data rows if the header is excluded |
| Codex | 23,288 rows; notes it would be 23,289 if the header counted as a row |
| pandas (`len(df)`) | **23,288** data rows |

Both agents were right, and both spontaneously disambiguated "file rows" vs
"data rows" — a distinction the question did not make.

The failure was mine. My initial baseline came from a newline-counting command
(`wc -l`), and this CSV has **no trailing newline on its last line**, so the count
came back one short. I carried that number into the audit as "ground truth" and
briefly scored a correct agent as wrong.

**Lesson:** file-format edge cases (missing trailing newline, BOM headers, trailing
spaces) sit below the abstraction layer both agents *and* auditors normally look at.
The agents handled this one better than the human did.

## 2. RFM segmentation: same method, same data, 2× different answer

**Question:** "Segment users into the 8 standard RFM classes."

| Segment | Kimi | Codex |
|---------|------|-------|
| High-value (R↑F↑M↑) | 948 | 653 |
| Develop | 100 | 74 |
| Retain | 587 | 220 |
| Win-back | 66 | 31 |
| ... | | |

Both totals = 3,399. Both internally consistent. Both *declared* their methodology
when asked. Reproduction showed:

- **Codex**: thresholds = mean, R ≤ mean counts as "high" → exactly reproduces 653/74/220/31...
- **Kimi**: thresholds = median, boundaries use ≥ → exactly reproduces 948/100/587/66...

Because this dataset has heavy-tailed F and M (a few whale users), mean ≫ median,
so hundreds of mid-range users flip segments depending on one silent choice.

**Lesson:** "use RFM" is not a specification. Threshold statistic and boundary
operator must be pinned by the human, or two correct agents will ship two
incompatible customer lists.

---

## 3. Churn definition: the smarter agent's answer is harder to audit

**Question:** "How many days without purchase counts as churned?"

- **Codex:** used mean R (585 days), noted you could substitute 90/180/365 by industry. Mechanical, safe.
- **Kimi:** observed median R = 434 days → "over half the users buy less than once
  a year — this looks like low-frequency / high-ticket retail" → proposed 730 days
  (1,153 users, 33.9%; verified numerically correct).

Kimi's chain of reasoning is what a senior analyst would do — but the business-context
inference is an *assumption stated as an observation*. It happens to be plausible.
Nothing in the data can confirm it.

**Lesson:** as agents get better at inference, their unverifiable claims become
fluent enough to pass review. Confidence is not evidence.

---

## 4. Recency (R): transparency without compatibility

**Question:** "Compute days-since-last-purchase for every user."

Both agents exported per-user tables **and declared their reference dates**:

- Codex: last transaction timestamp (2020-04-25 21:34) → 87% exact match with ground
  truth (residual = intra-day rounding).
- Kimi: day *after* the last transaction (2020-04-26) → every single value +1 day.

Neither is wrong. Both are auditable. They are still mutually incompatible, and any
downstream rule ("churn if R > 365") will classify a band of users differently.

**Lesson:** declared assumptions still need to be *unified* — declaring is the
agent's job; deciding is the human's.

---

## 5. Data-quality diagnosis: agents found real issues — and the auditor almost failed

Agents correctly and independently found: 1,174 zero-amount orders (5.0%),
one order id duplicated 3×, 2 fully duplicated rows, and (Codex) trailing spaces
in **all 23,288** order ids plus 68 order-ids whose embedded date contradicts the
transaction date.

The near-miss: when I verified the trailing-spaces claim, pandas type inference
had silently cast order ids to integers — stripping the spaces — and my check
found none. I briefly concluded Codex had hallucinated. Re-reading the file as
raw strings (`dtype=str`) confirmed Codex was exactly right.

**Lesson:** cross-validation is necessary but not sufficient — the verification
pipeline itself has failure modes, and tools' default behaviours (type inference,
encoding, newline handling) are a shared root cause across findings 1 and 5.

---
