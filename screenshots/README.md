# Screenshots

Original conversation screenshots. The experiments were conducted in Chinese, so the
prompts and answers are in Chinese — the numbers are language-independent, and the
tables below map each screenshot to the English scoreboard in the root README.

Agents: **Kimi** (K2.6 Agent) and **Codex** (OpenAI, GPT-5.5). Both write and execute
real code on the uploaded file.

## Codex

| File | Questions asked | Key content |
|------|-----------------|-------------|
| `q1_basics_and_q2_monthly_codex.png` | rows / distinct users / time range; highest-revenue month | **23,288 rows**, 3,399 users, 2015-02-12 15:04 → 2020-04-25 21:34; highest month **2019-12 = 10,030,508**. Volunteers "23,289 if the header counts as a row" — disambiguating a distinction the question never made. |
| `q3_rfm_codex.png` | 8-class RFM segmentation | High-value **653**, develop 74, retain 220, win-back 31, potential 146, new 1095, keep 86, churned 1094. **Declares its caliber in the last line**: reference date 2020-04-25 21:34, thresholds = **mean**, `R ≤ mean` counts as high. |
| `q4_churn_and_q5_recency_codex.png` | Does F include the first purchase? / churn threshold / per-user R | F **includes** the first purchase; churn threshold **585 days (= mean R)**, noting 90/180/365 as industry alternatives; exports R for all 3,399 users with reference date **2020-04-25 21:34**. |
| `q6_data_quality_codex.png` | data-quality scan | Trailing space on **all 23,288 order ids**, one order id repeated 3× (2 redundant rows), **1,174 zero-amount records (5.04%)**, **68 order ids whose date prefix contradicts the transaction date**, 195 same-user/time/amount combinations — plus an explicit list of what it checked and found clean. All verified correct. |

## Kimi

| File | Questions asked | Key content |
|------|-----------------|-------------|
| `q1_users_kimi.png` | how many distinct users? | 3,399 users, **23,288 total orders**, mean 6.85 orders/user, most active user has 90 orders. |
| `q1_timerange_kimi.png` | time range? | 2015-02-12 15:04 → 2020-04-25 21:34; 1,797 distinct dates; busiest single day 2016-12-20 with 213 orders. |
| `q3_rfm_kimi.png` + `q3_rfm_kimi_part2.png` | 8-class RFM segmentation | High-value **948**, develop 100, retain 587, win-back 66, potential 109, new 544, keep 152, churned 893. **Declares its caliber up front**: reference date **2020-04-26**, thresholds = **median** (R ≤ 434 days, F ≥ 4, M ≥ 26,900). Part 2 adds derived groupings ("core quality customers" 1,535 = 45.2%). Compare with Codex's 653 — same method, different threshold statistic. |
| `q3b_frequency_definition_kimi.png` | does F include the first purchase? | Yes — `frequency = len(amounts)`, so a first-time buyer has F = 1. Offers to re-run excluding it. |
| `q4_churn_kimi.png` + `q4_churn_kimi_part2.png` | how many days without a purchase counts as churn? | Gives a full recency distribution (median 434 days, P75 960, P90 1,362), then a per-industry threshold table, then infers from the distribution that this "looks like low-frequency / high-ticket retail" and proposes **730 days** (1,153 users, 33.9%) as churn and 365 days (1,867, 54.9%) as high-risk. The inference is plausible, fluent — and unverifiable from the data alone. |
| `q5_recency_kimi.png` + `q5_recency_kimi_part2.png` | compute each user's R | Exports all 3,399 users using reference date **2020-04-26** — one day later than Codex, so every value is +1. Users who bought on the last day get R = 1 rather than 0. |
| `q6_data_quality_kimi.png` + `part2` + `part3` | data-quality scan | 1,174 zero-amount orders (5.0%), order id 201907130018 repeated 3×, 1 fully duplicated row, **362 extreme amounts**, **476 cases of the same user ordering within one minute** — plus a severity table and a prioritised remediation list. Finds real issues Codex did not flag (dense repeat ordering), and misses ones Codex caught (trailing spaces, 68 date mismatches). |
