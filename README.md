# NFL Parlay Prediction & Analytics

An educational, portfolio-focused project for building and evaluating NFL probability models and parlay simulations. The goal is **calibrated probabilities and transparent evaluation**, not guaranteed betting profits.

## Project status

**Phase 1 — Data foundation (in progress)**

- [x] Repository initialized
- [x] Reproducible schedule and play-by-play download script
- [ ] Validate downloaded schemas and data quality
- [ ] Build leakage-safe pregame team features
- [ ] Train and evaluate a chronological baseline model
- [ ] Add correlated same-game parlay simulation
- [ ] Build a research dashboard

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/woodywu226/nfl-parlay-prediction.git
cd nfl-parlay-prediction
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
python scripts/download_data.py --seasons 2022 2023 2024 2025
```

The script writes Parquet files under `data/raw/`. Raw data is intentionally excluded from Git; rerun the script to reproduce it.

## Data

NFL play-by-play and schedule data are retrieved with [nflreadpy](https://github.com/nflverse/nflreadpy), from the nflverse data ecosystem. Review the upstream project's documentation and data terms before reuse or redistribution.

## Modeling principles

- Use chronological train/validation/test splits; never randomly mix future games into training.
- Construct pregame features only from information available before kickoff.
- Track feature timestamps to prevent temporal leakage.
- Evaluate probabilities with Brier score, log loss, and calibration, not accuracy alone.
- Do not multiply same-game leg probabilities as if they were independent. Model game-level dependence before estimating joint probability.
- Compare estimates with market prices while accounting for the bookmaker margin and uncertainty.

## Repository layout

```text
configs/                 Data and experiment configuration
data/raw/                Downloaded source data (gitignored)
data/processed/          Cleaned data (gitignored)
data/features/           Model-ready features (gitignored)
scripts/                 Reproducible command-line scripts
src/nfl_parlay/          Project Python package
tests/                   Automated tests
```

## Responsible use

This project is for learning, statistical research, and portfolio demonstration. Sports outcomes are uncertain; model estimates can be wrong, historical performance does not ensure future results, and betting can cause financial harm. Never treat model output as a guarantee or risk money you cannot afford to lose.
