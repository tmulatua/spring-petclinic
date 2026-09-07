#!/usr/bin/env python3
"""Synthetic Suspicious Activity Report (SAR) narrative snippets.

Template-based, offline, deterministic. To scale up diversity, drop an
Anthropic/OpenAI call inside render() (see TODO) — keep the seed loop so
outputs stay reproducible.

Usage: python3 text/generate_sar_narratives.py --n 50 --seed 42
"""
import argparse, json
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "output"

TYPOLOGIES = {
    "structuring": "multiple cash deposits of USD {amt} each kept just below the reporting threshold across {n_branch} branches within {days} days",
    "layering": "rapid movement of USD {amt} through {n_branch} shell entities with no clear business purpose, followed by outward remittance to {country}",
    "funnel": "cash deposits in {country} mirrored by same-day withdrawals of USD {amt} in a different jurisdiction",
    "mule": "account received USD {amt} from {n_branch} unrelated third parties and forwarded funds within 24 hours, retaining a small commission",
}

COUNTRIES = ["a high-risk jurisdiction", "an offshore financial center", "a neighboring country"]


def render(rng: np.random.Generator, i: int) -> dict:
    typ = rng.choice(list(TYPOLOGIES))
    template = TYPOLOGIES[typ]
    amt = int(rng.integers(5_000, 500_000))
    n_branch = int(rng.integers(2, 8))
    days = int(rng.integers(3, 30))
    country = COUNTRIES[rng.integers(0, len(COUNTRIES))]
    # TODO: replace template fill with an LLM rewrite for linguistic diversity:
    #   resp = anthropic.messages.create(..., messages=[{"role":"user",
    #   "content": f"Rewrite as a bank analyst's SAR narrative: {body}"}])
    body = template.format(amt=f"{amt:,}", n_branch=n_branch, days=days, country=country)
    return {
        "sar_id": f"SAR-SYN-{i:05d}",
        "typology": typ,
        "narrative": (
            f"Review identified activity consistent with potential {typ}: {body}. "
            "Transaction patterns deviate materially from the customer's stated profile. "
            "Recommend escalation for enhanced due diligence."
        ),
        "synthetic": True,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=50)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    rng = np.random.default_rng(args.seed)
    rows = [render(rng, i) for i in range(args.n)]
    OUT.mkdir(exist_ok=True)
    path = OUT / "sar_narratives.jsonl"
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} narratives -> {path}")


if __name__ == "__main__":
    main()
