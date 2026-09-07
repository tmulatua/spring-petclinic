#!/usr/bin/env python3
"""Generate synthetic customer accounts and transactions (AML-flavored).

Usage: python3 tabular/generate_transactions.py --n 1000 --seed 42
Output: output/transactions[_<seed>].csv, output/customers[_<seed>].csv
"""
import argparse, hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

OUT = Path(__file__).resolve().parent.parent / "output"

CHANNELS = ["wire", "ach", "cash", "crypto", "card"]
COUNTRIES = ["ID", "SG", "MY", "TH", "HK", "AE", "GB", "US"]
HIGH_RISK_COUNTRIES = {"AE", "HK"}


def fake_id(seed: int, i: int, prefix: str) -> str:
    """Deterministic pseudonymous ID — never a real identifier."""
    h = hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()[:10].upper()
    return f"{prefix}-{h}"


def generate(n_customers: int, n_txns: int, seed: int):
    rng = np.random.default_rng(seed)
    fake = Faker()
    Faker.seed(seed)

    customers = pd.DataFrame({
        "customer_id": [fake_id(seed, i, "CUST") for i in range(n_customers)],
        "segment": rng.choice(["retail", "sme", "corporate"], n_customers, p=[0.7, 0.2, 0.1]),
        "country": rng.choice(COUNTRIES, n_customers),
        "kyc_risk_rating": rng.choice(["low", "medium", "high"], n_customers, p=[0.6, 0.3, 0.1]),
        "onboard_date": [fake.date_between(start_date="-5y", end_date="-1m") for _ in range(n_customers)],
    })

    cust_idx = rng.integers(0, n_customers, n_txns)
    # Log-normal amounts; ~2% are structuring-like (just below 10k reporting threshold)
    amounts = rng.lognormal(mean=7.5, sigma=1.6, size=n_txns).round(2)
    struct_mask = rng.random(n_txns) < 0.02
    amounts[struct_mask] = rng.uniform(9000, 9999, struct_mask.sum()).round(2)

    txns = pd.DataFrame({
        "txn_id": [fake_id(seed + 1, i, "TXN") for i in range(n_txns)],
        "customer_id": customers["customer_id"].values[cust_idx],
        "txn_date": [fake.date_between(start_date="-1y", end_date="today") for _ in range(n_txns)],
        "amount": amounts,
        "currency": "IDR",
        "channel": rng.choice(CHANNELS, n_txns, p=[0.3, 0.25, 0.15, 0.1, 0.2]),
        "counterparty_country": rng.choice(COUNTRIES, n_txns),
        "_synthetic_structuring": struct_mask,  # label for eval only — strip before training use
    })
    return customers, txns


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=1000, help="number of transactions")
    p.add_argument("--customers", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--suffix", action="store_true", help="append seed to filenames")
    args = p.parse_args()

    customers, txns = generate(args.customers, args.n, args.seed)
    OUT.mkdir(exist_ok=True)
    tag = f"_{args.seed}" if args.suffix else ""
    customers.to_csv(OUT / f"customers{tag}.csv", index=False)
    txns.to_csv(OUT / f"transactions{tag}.csv", index=False)
    print(f"customers: {len(customers)}  transactions: {len(txns)}  -> {OUT}")


if __name__ == "__main__":
    main()
