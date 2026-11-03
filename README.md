# NFL Parlay Prediction & Analytics

An NFL data science portfolio project focused on reproducible data pipelines, **pregame feature engineering**, probability calibration, and eventually correlated same-game event simulations.

**Current scope:** historical data processing and feature engineering are implemented and have been run locally on real nflverse data. A trained prediction model, validated win probabilities, and parlay simulator are **not yet available**. This is a research project, not a system for guaranteed betting returns.

## Project progress

| Stage | Status | Deliverable |
| --- | --- | --- |
| 1. Data acquisition | Complete | Reproducible NFL schedules and play-by-play downloader |
| 2. Feature engineering | Implemented and locally executed | Team-game and matchup Parquet feature tables |
| 2.5. Data validation | In progress | Structural checks complete; full temporal leakage audit pending |
| 3. Win probability modeling | Planned | Chronological baseline model and calibrated probability evaluation |
| 4. Correlated event simulation | Planned | Dependence-aware joint probability estimation |
| 5. Dashboard | Planned | Interactive model evaluation and research UI |

### Latest local feature-build results

The feature pipeline was run locally using NFL seasons **2022–2025**:

| Output / check | Observed result |
| --- | ---: |
| Team-game records | 2,174 |
| Matchup records | 1,087 |
| Pregame feature columns | 16 |
| Total matchup-table columns | 22 |
| Duplicate matchup game IDs | 0 |
| 2022 / 2023 / 2024 / 2025 matchups | 271 / 272 / 272 / 272 |
| Missing pregame feature cells | 256 (all in 2022) |

These counts are **local execution observations**, not files committed to this repository. The 2022 season has 271 completed games because the Bills–Bengals game was canceled. The 256 missing feature cells correspond to 16 features for the 16 opening-week matchups in 2022; later seasons inherit trailing historical team games. These checks do **not** establish that the pipeline is fully free of data leakage.

## Quick start (macOS / Linux)

Requires Python 3.10+ and Git. Run commands from a terminal:

```bash
git clone https://github.com/woodywu226/nfl-parlay-prediction.git
cd nfl-parlay-prediction

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"

python3 scripts/download_data.py --seasons 2022 2023 2024 2025
python3 scripts/build_features.py
python3 -m pytest -v
```

If the virtual environment is active, `python` should also work. Using `python3` explicitly avoids the common macOS `zsh: command not found: python` error when no virtual environment is active.

The download step writes source Parquet data to `data/raw/`. The feature builder writes:

- `data/features/team_game_features.parquet`
- `data/features/matchup_features.parquet`

The generated datasets are ignored by Git. Running the pipeline locally does **not** automatically update GitHub; code or documentation changes must be committed and pushed.

## Data sources and reproducibility

Historical schedules and play-by-play data come from [nflverse](https://github.com/nflverse/nflverse-data), accessed through [nflreadpy](https://github.com/nflverse/nflreadpy). Consult the upstream dataset-specific license terms before redistributing source data.

A small, readable [2024 Week 1 results sample](data/sample/2024_week1_games.csv) is intended for inspection, not model training.

A reproducible exporter creates the **2024 regular-season Weeks 1–17** results dataset (256 games):

```bash
python3 scripts/export_2024_results.py
```

The exported results are available at [data/processed/2024_regular_season_results.csv](data/processed/2024_regular_season_results.csv). A GitHub Actions workflow can regenerate the export.

## Feature engineering

Implemented in `src/nfl_parlay/features.py`, with a CLI entry point at `scripts/build_features.py`.

The pipeline first computes one record per team per game, then joins home and away histories to create one matchup record per game. It generates **16 pregame features** (eight for each team):

| Feature family | Team-level pregame measurements |
| --- | --- |
| Scoring | Points for, points against |
| Offense | EPA per play, success rate, yards per play |
| Defense | EPA per play allowed, success rate allowed |
| Ball security | Turnovers, where source fields are available |

Each rolling statistic uses the **five previous team games** and shifts by one completed game so the current game is excluded. The rolling history can cross season boundaries; bye weeks do not count as games. Missing early-history values remain null.

**Important limitation:** a shift-based implementation is a useful safeguard but is not a complete proof of temporal correctness. Before training, verify source ordering, postponed games, kickoff timestamps, input availability, and any same-game statistics that could accidentally enter predictors. Do not use current-game scores or play-by-play outcomes as pregame inputs.

## Planned modeling and evaluation

The first model will estimate **home-team win probability**, before attempting player props or same-game parlays.

- **Training:** 2022–2023 seasons
- **Validation:** 2024 season
- **Held-out test:** 2025 season
- **Baseline:** logistic regression, with appropriate preprocessing
- **Metrics:** Brier score, log loss, ROC-AUC, and calibration diagnostics
- **Comparisons:** simple baselines and, later, more flexible models

A target-label construction step still needs to join completed game results to the matchup feature table. The held-out 2025 test set must not be used for model selection.

For eventual multi-leg estimates, same-game events are dependent. Joint probabilities must account for that dependence rather than multiplying individual leg probabilities under an unjustified independence assumption. Historical backtests should account for market margin, data availability, and uncertainty.

## Repository structure

```text
.github/workflows/       Automated checks and data-export workflow
configs/                 Data configuration
data/raw/                Downloaded NFL source data (gitignored)
data/processed/          Processed datasets (mostly gitignored)
data/features/           Generated model-ready features (gitignored)
scripts/                 Download, export, and feature-building CLIs
src/nfl_parlay/          Reusable Python package
tests/                   Automated tests
```

## Responsible use

This project is intended for learning, statistical research, and portfolio demonstration. Model predictions are uncertain, historical performance does not guarantee future performance, and betting involves financial risk. No model or simulation should be treated as a guarantee of profit.
