"""Reproduces BOTH agents' RFM segmentations exactly.

Demonstrates finding #2: identical data + identical method name ("RFM"),
two silent definition choices -> 2x different segment sizes.

    python rfm_threshold_reproduction.py path/to/orders.csv
"""
import sys

import pandas as pd

LABELS = {
    (1, 1, 1): "high-value", (1, 0, 1): "develop", (0, 1, 1): "retain", (0, 0, 1): "win-back",
    (1, 1, 0): "potential", (1, 0, 0): "new", (0, 1, 0): "keep", (0, 0, 0): "churned",
}


def segment(g, r_high, f_high, m_high, tag):
    seg = pd.Series(
        [LABELS[k] for k in zip(r_high.astype(int), f_high.astype(int), m_high.astype(int))],
        index=g.index,
    )
    print(f"\n-- {tag} --")
    print(seg.value_counts().to_string())


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "orders.csv")
    df.columns = [c.strip().lstrip("﻿") for c in df.columns]
    df["trans_date"] = pd.to_datetime(df["trans_date"])
    ref = df["trans_date"].max()
    g = df.groupby("id").agg(F=("order_id", "count"), M=("amount", "sum"), last=("trans_date", "max"))
    g["R"] = (ref - g["last"]).dt.days

    # Codex's silent choices: mean thresholds, R <= mean is high
    segment(g, g["R"] <= g["R"].mean(), g["F"] >= g["F"].mean(), g["M"] >= g["M"].mean(),
            "Codex reproduction: mean thresholds")

    # Kimi's silent choices: median thresholds, boundaries with >= / <=
    segment(g, g["R"] <= g["R"].median(), g["F"] >= g["F"].median(), g["M"] >= g["M"].median(),
            "Kimi reproduction: median thresholds, >= boundaries")

    print(
        "\nWhy they diverge: heavy-tailed F and M (whale users) push the mean far"
        "\nabove the median, so hundreds of mid-range users flip between segments"
        "\ndepending on one undeclared statistic."
    )
