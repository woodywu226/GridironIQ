# NFL Parlay Prediction & Analytics

An educational, portfolio-focused project for building and evaluating NFL probability models and parlay simulations. The goal is **calibrated probabilities and transparent evaluation**, not guaranteed betting profits.

## Project status

**Phase 2 — Feature engineering (in progress)**

- [x] Repository initialized
- [x] Reproducible schedule and play-by-play download script
- [x] Export and validate 2024 regular-season results (Weeks 1-17)
- [x] Build leakage-safe pregame team and matchup feature pipeline
- [ ] Validate feature pipeline against a full multi-season nflverse download
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
python scripts/build_features.py
pytest
```

The downloader writes source Parquet files under `data/raw/`. The feature builder writes `team_game_features.parquet` and `matchup_features.parquet` under `data/features/`. Both directories are gitignored because the source and derived datasets can be regenerated.

## Data

### Included real-data sample

The repository includes [2024 Week 1 NFL game results](data/sample/2024_week1_games.csv): 16 completed regular-season games with real final scores, home/away teams, dates, and home-team score differential. This is a small, human-readable sample for checking the project structure—not a statistically sufficient training set.

The sample is based on the [nflverse schedules dataset](https://github.com/nflverse/nflverse-data), which publishes NFL game and schedule data. The nflverse project identifies most of its datasets (excluding specifically marked exceptions such as FTN data) as CC BY 4.0; retain attribution and check the dataset-specific terms before redistribution.

To export all completed 2024 regular-season results from Weeks 1–17 (256 games), run:

```bash
python scripts/export_2024_results.py
```

This writes `data/processed/2024_regular_season_results.csv`. The script validates the expected game count, unique game IDs, and home-score margin before writing. You can also run the **Export 2024 NFL results** workflow from the GitHub Actions tab to fetch and commit the CSV to the repository.

### Full historical data

NFL play-by-play and schedule data are retrieved with [nflreadpy](https://github.com/nflverse/nflreadpy). Run the downloader in Quick start to retrieve the selected seasons into `data/raw/`. The full raw files are intentionally not committed because play-by-play data are large and should be reproducibly downloaded from the source.

## Feature engineering

`src/nfl_parlay/features.py` builds one row per team/game, then joins home and away histories into one row per game. Current features include:

- Trailing five-game points scored and allowed
- Offensive EPA/play, success rate, and yards/play
- Defensive EPA/play and success rate allowed
- Turnovers (interceptions plus lost fumbles), when those columns exist in the source

Every rolling feature is shifted by one game. A team's Week 5 feature therefore uses only its completed games before Week 5; it never includes Week 5's result. Early-season histories remain null rather than being filled with future or same-game information. Bye weeks are naturally skipped because the rolling window counts prior team games, not calendar weeks.

The output retains game outcomes in the team-game table for later target construction. Do not use `points_for`, `points_against`, or other same-game observed statistics as predictors for that same game.

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
