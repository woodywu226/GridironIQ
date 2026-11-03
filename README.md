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

### Included real-data sample

The repository includes [2024 Week 1 NFL game results](data/sample/2024_week1_games.csv): 16 completed regular-season games with real final scores, home/away teams, dates, and home-team score differential. This is a small, human-readable sample for checking the project structure—not a statistically sufficient training set.

The sample is based on the [nflverse schedules dataset](https://github.com/nflverse/nflverse-data), which publishes NFL game and schedule data. The nflverse project identifies most of its datasets (excluding specifically marked exceptions such as FTN data) as CC BY 4.0; retain attribution and check the dataset-specific terms before redistribution.

### Full historical data

NFL play-by-play and schedule data are retrieved with [nflreadpy](https://github.com/nflverse/nflreadpy). Run the downloader in Quick start to retrieve the selected seasons into `data/raw/`. The full raw files are intentionally not committed because play-by-play data are large and should be reproducibly downloaded from the source.

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
