from pathlib import Path

import polars as pl


def test_parquet_round_trip(tmp_path: Path) -> None:
    """Smoke-test Parquet serialization without requiring a network download."""
    sample = pl.DataFrame({"game_id": ["2024_01_KC_BAL"], "season": [2024]})
    output = tmp_path / "sample.parquet"
    sample.write_parquet(output)

    restored = pl.read_parquet(output)
    assert restored.height == 1
    assert restored.get_column("game_id").item() == "2024_01_KC_BAL"


def test_gitignore_keeps_data_directories_empty_in_repo() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert "data/raw/*" in gitignore
    assert "!data/raw/.gitkeep" in gitignore


def test_real_week_one_sample_has_valid_scores() -> None:
    """Validate the committed, real 2024 Week 1 results sample."""
    sample_path = Path("data/sample/2024_week1_games.csv")
    games = pl.read_csv(sample_path)

    assert games.height == 16
    assert games.get_column("game_id").n_unique() == 16
    assert games.get_column("season").unique().to_list() == [2024]
    assert (games.get_column("home_score") - games.get_column("away_score")).to_list() == games.get_column("result").to_list()
