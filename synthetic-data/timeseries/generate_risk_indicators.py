#!/usr/bin/env python3
"""Synthetic daily risk-indicator time series with regime switching.

Usage: python3 timeseries/generate_risk_indicators.py --days 365 --seed 42
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "output"


def generate(days: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    regimes = rng.choice([0, 1, 2], days, p=[0.7, 0.25, 0.05])  # calm / stress / crisis
    vol = np.choose(regimes, [0.01, 0.03, 0.08])

    returns = rng.normal(-0.0002, vol)
    alert_rate = np.clip(np.choose(regimes, [4, 12, 35]) + rng.normal(0, 2, days), 0, None).round()
    liquidity = 100 + np.cumsum(returns * 100)  # random-walk liquidity coverage proxy

    return pd.DataFrame({
        "date": pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D"),
        "regime_label": regimes,
        "daily_return": np.round(returns, 5),
        "aml_alerts": alert_rate.astype(int),
        "liquidity_index": np.round(liquidity, 2),
    })


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=365)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    df = generate(args.days, args.seed)
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / "risk_indicators.csv", index=False)
    print(f"{len(df)} days -> {OUT / 'risk_indicators.csv'}")


if __name__ == "__main__":
    main()
