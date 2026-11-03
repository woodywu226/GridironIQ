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
