"""Ground-truth audit baseline.

Recomputes every quantity the agents were asked about, using explicit,
pinned definitions. Run against the raw CSV (not distributed in this repo):

    python audit_baseline.py path/to/orders.csv

Definitions pinned here:
- reference date  = max transaction timestamp in the data
- R               = whole days between reference date and user's last purchase
- F               = number of orders (zero-amount included)
- M               = total amount
- RFM high/low    = mean threshold, R <= mean is "high"
- retention day N = share of all users with an order exactly N days after
                    their first purchase date
"""
import sys

import numpy as np
import pandas as pd


def load(path: str) -> pd.DataFrame:
    # dtype=str for order_id: pandas type inference would strip the trailing
    # spaces we need to detect (see findings.md #5).
    df = pd.read_csv(path, dtype={"order_id": str})
    df.columns = [c.strip().lstrip("﻿") for c in df.columns]
    df["trans_date"] = pd.to_datetime(df["trans_date"])
    return df


def data_quality(df: pd.DataFrame) -> None:
    print("== data quality ==")
    print("rows:", len(df), "| dedup:", len(df.drop_duplicates()))
    print("users:", df["id"].nunique(), "| distinct order ids:", df["order_id"].str.strip().nunique())
    print("time range:", df["trans_date"].min(), "->", df["trans_date"].max())
    print("nulls:", int(df.isna().sum().sum()))
    print("zero-amount:", int((df["amount"] == 0).sum()))
    print("trailing-space order ids:", int(df["order_id"].str.endswith(" ").sum()))
    oid = df["order_id"].str.strip()
    mism = (oid.str[:8] != df["trans_date"].dt.strftime("%Y%m%d")).sum()
    print("order-id date prefix mismatches:", int(mism))


def rfm(df: pd.DataFrame) -> pd.Series:
    print("\n== RFM (mean thresholds, R<=mean high) ==")
    ref = df["trans_date"].max()
    g = df.groupby("id").agg(F=("order_id", "count"), M=("amount", "sum"), last=("trans_date", "max"))
    g["R"] = (ref - g["last"]).dt.days
    rh, fh, mh = g["R"] <= g["R"].mean(), g["F"] >= g["F"].mean(), g["M"] >= g["M"].mean()
    labels = {
        (1, 1, 1): "high-value", (1, 0, 1): "develop", (0, 1, 1): "retain", (0, 0, 1): "win-back",
        (1, 1, 0): "potential", (1, 0, 0): "new", (0, 1, 0): "keep", (0, 0, 0): "churned",
    }
    seg = pd.Series(
        [labels[k] for k in zip(rh.astype(int), fh.astype(int), mh.astype(int))], index=g.index
    )
    print(seg.value_counts().to_string())
    return seg


def retention(df: pd.DataFrame) -> None:
    print("\n== repurchase retention (cohort = first purchase day) ==")
    df = df.copy()
    df["day"] = df["trans_date"].dt.floor("D")
    first = df.groupby("id")["day"].min().rename("cohort")
    d = df.merge(first, on="id")
    d["gap"] = (d["day"] - d["cohort"]).dt.days
    total = df["id"].nunique()
    for n in (1, 7, 14):
        ret = d.loc[d["gap"] == n, "id"].nunique()
        print(f"day {n:>2}: {ret}/{total} = {ret / total:.2%}")


def ltv_90d(df: pd.DataFrame) -> None:
    print("\n== 90-day LTV (BG/NBD x Gamma-Gamma) ==")
    from lifetimes import BetaGeoFitter, GammaGammaFitter
    from lifetimes.utils import summary_data_from_transaction_data

    s = summary_data_from_transaction_data(df, "id", "trans_date", monetary_value_col="amount")
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(s["frequency"], s["recency"], s["T"])
    rep = s[(s["frequency"] > 0) & (s["monetary_value"] > 0)].copy()
    ggf = GammaGammaFitter(penalizer_coef=0.001)
    ggf.fit(rep["frequency"], rep["monetary_value"])
    rep["pred_amt"] = ggf.conditional_expected_average_profit(rep["frequency"], rep["monetary_value"])
    rep["ltv90"] = bgf.predict(90, rep["frequency"], rep["recency"], rep["T"]) * rep["pred_amt"]
    print(f"predictable users: {len(rep)}/{len(s)}")
    print(f"mean {rep['ltv90'].mean():.0f} | median {rep['ltv90'].median():.0f}")
    print("top 5:")
    print(rep.sort_values("ltv90", ascending=False)[["frequency", "pred_amt", "ltv90"]].head().round(0).to_string())
    print("NOTE: no acquisition-cost field in the data -> LTV only, ROI not computable.")


if __name__ == "__main__":
    frame = load(sys.argv[1] if len(sys.argv) > 1 else "orders.csv")
    data_quality(frame)
    rfm(frame)
    retention(frame)
    ltv_90d(frame)
