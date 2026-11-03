"""Leakage-safe pregame team and matchup feature engineering."""

from __future__ import annotations

from pathlib import Path

import polars as pl

SCHEDULE_COLUMNS = [
    "game_id", "season", "week", "game_type", "gameday",
    "home_team", "away_team", "home_score", "away_score",
]
PBP_REQUIRED = ["game_id", "posteam", "epa", "success", "yards_gained"]
ROLLING_SOURCE_COLUMNS = [
    "points_for", "points_against", "off_epa_per_play",
    "off_success_rate", "off_yards_per_play", "def_epa_per_play_allowed",
    "def_success_rate_allowed", "turnovers",
]


def _require_columns(frame: pl.DataFrame, required: list[str], name: str) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def build_team_game_stats(
    schedules: pl.DataFrame,
    pbp: pl.DataFrame,
) -> pl.DataFrame:
    """Create one row per team/game from completed regular-season games.

    Game outcomes are retained as labels/observed game stats. They are shifted
    before becoming rolling pregame features, so a game never predicts itself.
    """
    _require_columns(schedules, SCHEDULE_COLUMNS, "schedules")
    _require_columns(pbp, PBP_REQUIRED, "play-by-play")

    games = schedules.filter(
        (pl.col("game_type") == "REG")
        & pl.col("home_score").is_not_null()
        & pl.col("away_score").is_not_null()
    ).select(SCHEDULE_COLUMNS)

    turnover_exprs: list[pl.Expr] = []
    if "interception" in pbp.columns:
        turnover_exprs.append(pl.col("interception").cast(pl.Int64).sum().alias("interceptions"))
    if "fumble_lost" in pbp.columns:
        turnover_exprs.append(pl.col("fumble_lost").cast(pl.Int64).sum().alias("fumbles_lost"))

    offense = pbp.filter(pl.col("posteam").is_not_null()).group_by(
        ["game_id", "posteam"]
    ).agg(
        pl.col("epa").mean().alias("off_epa_per_play"),
        pl.col("success").cast(pl.Float64).mean().alias("off_success_rate"),
        pl.col("yards_gained").mean().alias("off_yards_per_play"),
        pl.len().alias("offensive_plays"),
        *turnover_exprs,
    ).rename({"posteam": "team"})

    turnover_columns = [c for c in ["interceptions", "fumbles_lost"] if c in offense.columns]
    if turnover_columns:
        offense = offense.with_columns(
            pl.sum_horizontal([pl.col(c).fill_null(0) for c in turnover_columns]).alias("turnovers")
        )
    else:
        offense = offense.with_columns(pl.lit(None, dtype=pl.Float64).alias("turnovers"))

    home = games.select(
        "game_id", "season", "week", "gameday",
        pl.col("home_team").alias("team"),
        pl.col("away_team").alias("opponent"),
        pl.col("home_score").alias("points_for"),
        pl.col("away_score").alias("points_against"),
        pl.lit(1).alias("is_home"),
    )
    away = games.select(
        "game_id", "season", "week", "gameday",
        pl.col("away_team").alias("team"),
        pl.col("home_team").alias("opponent"),
        pl.col("away_score").alias("points_for"),
        pl.col("home_score").alias("points_against"),
        pl.lit(0).alias("is_home"),
    )
    team_games = pl.concat([home, away]).join(
        offense, on=["game_id", "team"], how="left"
    )
    opponent_offense = offense.rename(
        {
            "team": "opponent",
            "off_epa_per_play": "def_epa_per_play_allowed",
            "off_success_rate": "def_success_rate_allowed",
        }
    ).select(
        "game_id", "opponent",
        "def_epa_per_play_allowed", "def_success_rate_allowed",
    )
    return team_games.join(opponent_offense, on=["game_id", "opponent"], how="left").sort(
        ["team", "gameday", "week", "game_id"]
    )


def add_rolling_pregame_features(
    team_games: pl.DataFrame,
    window: int = 5,
) -> pl.DataFrame:
    """Add trailing team averages using only games completed before each row."""
    if window < 1:
        raise ValueError("window must be at least 1")
    _require_columns(team_games, ["team", "gameday", *ROLLING_SOURCE_COLUMNS], "team games")
    ordered = team_games.sort(["team", "gameday", "week", "game_id"])
    rolling_exprs = [
        pl.col(column)
        .rolling_mean(window_size=window, min_samples=1)
        .shift(1)
        .over("team")
        .alias(f"pregame_{column}_last{window}")
        for column in ROLLING_SOURCE_COLUMNS
    ]
    return ordered.with_columns(rolling_exprs)


def build_matchup_features(team_features: pl.DataFrame) -> pl.DataFrame:
    """Join home/away pregame features into one row per scheduled game."""
    feature_columns = [
        column for column in team_features.columns
        if column.startswith("pregame_")
    ]
    base = team_features.filter(pl.col("is_home") == 1).select(
        "game_id", "season", "week", "gameday",
        pl.col("team").alias("home_team"),
        pl.col("opponent").alias("away_team"),
        *[pl.col(c).alias(f"home_{c}") for c in feature_columns],
    )
    away = team_features.filter(pl.col("is_home") == 0).select(
        "game_id", *[pl.col(c).alias(f"away_{c}") for c in feature_columns]
    )
    return base.join(away, on="game_id", how="inner").sort(
        ["season", "week", "gameday", "game_id"]
    )


def build_feature_tables(
    schedules: pl.DataFrame,
    pbp: pl.DataFrame,
    window: int = 5,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Return team-game history and one-row-per-game pregame features."""
    team_games = build_team_game_stats(schedules, pbp)
    team_features = add_rolling_pregame_features(team_games, window=window)
    return team_features, build_matchup_features(team_features)


def main() -> None:
    raw_dir = Path("data/raw")
    output_dir = Path("data/features")
    schedules_path = raw_dir / "schedules.parquet"
    pbp_path = raw_dir / "play_by_play.parquet"
    if not schedules_path.exists() or not pbp_path.exists():
        raise SystemExit(
            "Raw data not found. Run: python scripts/download_data.py --seasons 2022 2023 2024 2025"
        )

    schedules = pl.read_parquet(schedules_path)
    pbp = pl.read_parquet(pbp_path)
    team_features, matchup_features = build_feature_tables(schedules, pbp)
    output_dir.mkdir(parents=True, exist_ok=True)
    team_features.write_parquet(output_dir / "team_game_features.parquet")
    matchup_features.write_parquet(output_dir / "matchup_features.parquet")
    print(f"Team-game rows: {team_features.height:,}")
    print(f"Matchup rows: {matchup_features.height:,}")
    print(f"Pregame features: {len([c for c in matchup_features.columns if c.startswith(('home_pregame_', 'away_pregame_'))])}")
    print(f"Saved features under {output_dir}/")


if __name__ == "__main__":
    main()
