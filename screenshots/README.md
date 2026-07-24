# Screenshots

Original conversation screenshots. The experiments were conducted in Chinese, so the
prompts and answers are in Chinese — but the numbers are language-independent, and the
table below maps each screenshot to the English scoreboard in the root README.

| File | Questions asked | Key content |
|------|-----------------|-------------|
| `q1_basics_and_q2_monthly_codex.png` | "How many rows / distinct users / time range?" and "Which month had the highest revenue?" | Answers **23,288 rows**, 3,399 users, 2015-02-12 15:04 → 2020-04-25 21:34; highest month **2019-12 = 10,030,508**. It also volunteers "23,289 if the header counts as a row" — the same row-count edge case Kimi got wrong in the other direction (23,287). |
| `q3_rfm_codex.png` | "Segment users into the 8 RFM classes — how many in each?" | High-value **653**, develop 74, retain 220, win-back 31, potential 146, new 1095, keep 86, churned 1094. **Declares its caliber in the last line**: reference date = 2020-04-25 21:34, thresholds = mean, `R ≤ mean` counts as high. That single choice is what separates it from Kimi's median-based 948. |
| `q4_churn_and_q5_recency_codex.png` | "Does F include the first purchase?", "How many days without a purchase counts as churn?", "Compute each user's R value" | Confirms F **includes** the first purchase; sets the churn threshold at **585 days (= mean R)** while noting 90/180/365 are common industry alternatives; exports per-user R for all 3,399 users using 2020-04-25 21:34 as the reference date (Kimi used 2020-04-26 → every value +1 day). |
| `q6_data_quality_codex.png` | "Are there any data-quality problems?" | Finds a **trailing space on all 23,288 order ids**, one order repeated 3× (2 redundant rows), **1,174 zero-amount records (5.04%)**, **68 order ids whose embedded date contradicts the transaction date**, and 195 same-user/time/amount combinations. It also lists what it checked and found clean. All verified correct — see `findings.md` #5 for how the trailing-space claim was nearly misjudged during the audit. |

Kimi's answers are quoted in the root README scoreboard and in `findings.md`.
