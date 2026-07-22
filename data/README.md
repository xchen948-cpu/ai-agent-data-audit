# Data

The raw dataset is **not distributed** in this repository (provided by an
internship program; redistribution rights unclear).

## Schema

`orders.csv` — ~23,288 rows, 3,399 distinct users, 2015-02 to 2020-04.

| column | type | notes |
|--------|------|-------|
| trans_date | datetime | `2020/4/25 21:34` format |
| id | int | user id (9 digits) |
| order_id | string | `YYYYMMDD` + sequence, 12 digits; **every value carries a trailing space** |
| amount | int | order amount; 5% of rows are 0 |

## Known quirks (intentionally preserved — they are part of the experiment)

- no trailing newline at end of file (breaks newline-counting row counts)
- BOM on the first header field
- trailing space on every `order_id`
- 1,174 zero-amount orders
- one order id duplicated 3× (2 fully duplicated rows)
- 68 order ids whose embedded date contradicts `trans_date`

Any structurally similar order-log dataset will reproduce the qualitative
findings; the scripts in [`ground_truth/`](../ground_truth/) only assume the
four columns above.
