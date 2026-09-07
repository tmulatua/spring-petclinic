# Synthetic Data Guide — Step-by-Step

This document explains environment setup, running generators, privacy checks, and next steps for synthetic data (AML / SupTech context).

## 1) Where we put things
- Root folder: synthetic-data/
- Subfolders:
  - synthetic-data/tabular
  - synthetic-data/timeseries
  - synthetic-data/text
  - synthetic-data/eval
  - synthetic-data/privacy
  - synthetic-data/output (gitignored)

## 2) Files added
- tabular/generate_transactions.py — tabular synthetic customers + transactions
- timeseries/generate_risk_indicators.py — daily risk indicators with regimes
- text/generate_sar_narratives.py — SAR narrative templates
- privacy/disclosure_metrics.py — DCR (distance to closest real record)
- eval/golden_dataset_template.jsonl — benchmark cases
- README.md — usage and layout

## 3) Why seeds and deterministic IDs
- Reproducibility for experiments and versioning
- Deterministic pseudonymous IDs avoid real identifiers

## 4) Environment setup (one-time)
- Use conda/mamba to avoid binary linking issues with numpy/pandas.
- Example:
  - Install Mambaforge/Miniforge
  - Create env: mamba create -y -n syndata python=3.11 numpy pandas faker
  - Activate: conda activate syndata
  - Or call python directly: /path/to/mambaforge/envs/syndata/bin/python <script>

## 5) How to run generators
- Tabular: python synthetic-data/tabular/generate_transactions.py --n 1000 --seed 42
- Alternate tabular (different seed, keep file): python synthetic-data/tabular/generate_transactions.py --n 1000 --seed 7 --suffix
- Time series: python synthetic-data/timeseries/generate_risk_indicators.py --days 365 --seed 42
- SAR narratives: python synthetic-data/text/generate_sar_narratives.py --n 50 --seed 42
- Privacy check (DCR): python synthetic-data/privacy/disclosure_metrics.py --real output/transactions.csv --synthetic output/transactions_7.csv --cols amount

## 6) Expected outputs
- customers.csv, transactions.csv, risk_indicators.csv, sar_narratives.jsonl in synthetic-data/output

## 7) Using datasets safely
- Do not include real PII in outputs.
- Keep training, test, and benchmark datasets separate (use different seeds).
- Remove evaluation-only labels (e.g., _synthetic_structuring) before training.

## 8) How to extend
- Tabular: use SDV to learn joint distributions from curated real samples (with approvals).
- Time series: sdv.timeseries or TimeGAN for realistic temporal patterns.
- Text: template -> LLM paraphrase (post-process to remove any real names).
- Evaluation: expand golden_dataset_template.jsonl with adversarial tests and hallucination probes.

## 9) Privacy and compliance (recommended)
- Run disclosure risk tests: nearest neighbor, attribute inference.
- Apply differential privacy or calibrated noise for shared outputs.
- Keep audit trails: seed, script version, disclosure metrics.

## 10) Troubleshooting
- libgfortran / numpy import errors: use a dedicated conda env (syndata).
- Probability sum errors in numpy.choice: ensure probabilities sum to 1.

## 11) Next actions (pick one)
- A) Guide through installing and activating the syndata env.
- B) Convert tabular generator to SDV with a provided sample (script + privacy steps).
- C) Add an LLM paraphrasing step with API integration and safeguards.
- D) Expand privacy checks (k-anonymity, inference risk, auditor report).
