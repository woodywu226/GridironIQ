import polars as pl
import pytest

from nfl_parlay.features import (
    add_rolling_pregame_features,
    build_feature_tables,
)


def _synthetic_inputs() -> tuple[pl.DataFrame, pl.DataFrame]:
    schedules = pl.DataFrame(
        {
            "game_id": ["g1", "g2", "g3"],
            "season": [2024, 2024, 2024],
            "week": [1, 2, 3],
            "game_type": ["REG", "REG", "REG"],
            "gameday": ["2024-09-08", "2024-09-15", "2024-09-22"],
            "home_team": ["DET", "MIN", "DET"],
            "away_team": ["MIN", "DET", "CHI"],
            "home_score": [20, 10, 30],
            "away_score": [10, 20, 14],
        }
    )
    pbp = pl.DataFrame(
        {
            "game_id": ["g1", "g1", "g2", "g2", "g3", "g3"],
            "posteam": ["DET", "MIN", "MIN", "DET", "DET", "CHI"],
            "epa": [0.2, -0.2, -0.1, 0.1, 0.4, -0.3],
            "success": [1, 0, 0, 1, 1, 0],
            "yards_gained": [6, 3, 4, 5, 7, 2],
            "interception": [0, 0, 1, 0, 0, 0],
            "fumble_lost": [0, 0, 0, 0, 0, 0],
        }
    )
    return schedules, pbp


def test_rolling_features_exclude_current_game() -> None:
    rows = pl.DataFrame(
        {
            "team": ["DET", "DET", "DET"],
            "gameday": ["2024-09-08", "2024-09-15", "2024-09-22"],
            "week": [1, 2, 3],
            "game_id": ["g1", "g2", "g3"],
            "points_for": [20.0, 10.0, 30.0],
            "points_against": [10.0, 20.0, 14.0],
            "off_epa_per_play": [0.2, 0.1, 0.4],
            "off_success_rate": [1.0, 1.0, 1.0],
            "off_yards_per_play": [6.0, 5.0, 7.0],
            "def_epa_per_play_allowed": [-0.2, -0.1, -0.3],
            "def_success_rate_allowed": [0.0, 0.0, 0.0],
            "turnovers": [0.0, 1.0, 0.0],
        }
    )
    result = add_rolling_pregame_features(rows, window=5)
    rolling = result["pregame_points_for_last5"].to_list()
    assert rolling[0] is None
    assert rolling[1] == pytest.approx(20.0)
    assert rolling[2] == pytest.approx(15.0)


def test_feature_tables_have_one_row_per_game_and_team() -> None:
    schedules, pbp = _synthetic_inputs()
    team, matchup = build_feature_tables(schedules, pbp)

    assert team.height == 6
    assert team.select("game_id", "team").n_unique() == 6
    assert matchup.height == 3
    assert matchup["game_id"].n_unique() == 3
    assert "home_pregame_points_for_last5" in matchup.columns
    assert "away_pregame_off_epa_per_play_last5" in matchup.columns


def test_current_game_score_is_not_used_as_current_pregame_feature() -> None:
    schedules, pbp = _synthetic_inputs()
    _, matchup = build_feature_tables(schedules, pbp)
    week_one = matchup.filter(pl.col("week") == 1).row(0, named=True)
    assert week_one["home_pregame_points_for_last5"] is None
    assert week_one["away_pregame_points_for_last5"] is None


def test_invalid_rolling_window_is_rejected() -> None:
    schedules, pbp = _synthetic_inputs()
    team, _ = build_feature_tables(schedules, pbp)
    with pytest.raises(ValueError, match="window"):
        add_rolling_pregame_features(team, window=0)
