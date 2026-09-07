#!/usr/bin/env python3
"""Basic disclosure-risk check: distance to closest real record (DCR).

Flags synthetic rows that are suspiciously close to real ones (memorization).

Usage:
  python3 privacy/disclosure_metrics.py --real real.csv --synthetic syn.csv \
      --cols amount,channel --threshold 0.01
"""
import argparse

import numpy as np
import pandas as pd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--real", required=True)
    p.add_argument("--synthetic", required=True)
    p.add_argument("--cols", required=True, help="comma-separated numeric cols to compare")
    p.add_argument("--threshold", type=float, default=0.01, help="min normalized distance")
    args = p.parse_args()

    real = pd.read_csv(args.real)
    syn = pd.read_csv(args.synthetic)
    cols = [c.strip() for c in args.cols.split(",")]

    R, S = real[cols].to_numpy(float), syn[cols].to_numpy(float)
    scale = R.max(axis=0) - R.min(axis=0) + 1e-9
    R, S = R / scale, S / scale

    dcr = np.sqrt(((S[:, None, :] - R[None, :, :]) ** 2).sum(-1)).min(axis=1)
    risky = (dcr < args.threshold).sum()
    print(f"rows checked:      {len(S)}")
    print(f"min DCR:           {dcr.min():.4f}")
    print(f"below threshold:   {risky} ({100*risky/len(S):.1f}%)")
    print("RESULT:", "FAIL — regenerate or add noise" if risky else "PASS")


if __name__ == "__main__":
    main()
