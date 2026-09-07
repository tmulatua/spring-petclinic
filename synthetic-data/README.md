# Synthetic Data Generators

Synthetic data for training, testing, and agent benchmarking (AML/SupTech use case).
All generators are **seeded and reproducible** — version the configs, not just outputs.

## Layout
```
tabular/       customer + transaction records (Faker/numpy)
timeseries/    daily risk indicators with regime switching (numpy)
text/          SAR narrative snippets (template-based; LLM hook optional)
eval/          golden dataset skeleton for agent benchmarking
privacy/       disclosure-risk metrics (nearest-neighbor distance)
output/        generated artifacts (gitignored)
```

## Quick start
```bash
python3 tabular/generate_transactions.py --n 1000 --seed 42
python3 timeseries/generate_risk_indicators.py --days 365 --seed 42
python3 text/generate_sar_narratives.py --n 50 --seed 42
python3 privacy/disclosure_metrics.py --real output/transactions.csv --synthetic output/transactions_2.csv
```

## Rules
- Training data, test fixtures, and eval/benchmark sets use **different seeds** — no leakage.
- Benchmark sets include adversarial/edge cases (see `eval/`).
- Run `privacy/` metrics before sharing any output derived from real data.
