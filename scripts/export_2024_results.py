"""Export completed 2024 regular-season games (Weeks 1-17) from nflverse."""

from pathlib import Path

import nflreadpy as nfl

OUTPUT = Path("data/processed/2024_regular_season_results.csv")
COLUMNS = [
    "game_id",
    "season",
    "week",
    "game_type",
    "gameday",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "result",
]


def main() -> None:
    schedules = nfl.load_schedules([2024])
    missing = [column for column in COLUMNS if column not in schedules.columns]
    if missing:
        raise ValueError(f"Unexpected nflverse schedule schema; missing columns: {missing}")

    games = (
        schedules
        .filter(
            (schedules["season"] == 2024)
            & (schedules["game_type"] == "REG")
            & schedules["week"].is_between(1, 17)
            & schedules["home_score"].is_not_null()
            & schedules["away_score"].is_not_null()
        )
        .select(COLUMNS)
        .sort(["week", "gameday", "game_id"])
    )

    if games.height != 272:
        raise RuntimeError(
            f"Expected 272 completed regular-season games for Weeks 1-17; "
            f"received {games.height}. Check upstream data before exporting."
        )

    # Verify the home-margin convention before writing.
    expected_margin = games["home_score"] - games["away_score"]
    if not expected_margin.equals(games["result"]):
        raise RuntimeError("Schedule result does not match home_score - away_score.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    games.write_csv(OUTPUT)
    print(f"Exported {games.height} games to {OUTPUT}")
    print(f"Weeks included: {games['week'].n_unique()} (1-17)")
    print(f"Unique game IDs: {games['game_id'].n_unique()}")


if __name__ == "__main__":
    main()
