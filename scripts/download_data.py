"""Download NFL schedules and play-by-play data to local Parquet files.

Usage:
    python scripts/download_data.py --seasons 2022 2023 2024 2025
"""
from __future__ import annotations

import argparse
from pathlib import Path

import nflreadpy as nfl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seasons",
        nargs="+",
        type=int,
        default=[2022, 2023, 2024, 2025],
        help="NFL seasons to download (e.g. --seasons 2022 2023 2024)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory for downloaded Parquet files (default: data/raw)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seasons = sorted(set(args.seasons))
    if not seasons or any(season < 1999 for season in seasons):
        raise SystemExit("Please provide valid NFL seasons (1999 or later).")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading seasons: {seasons}")
    schedules = nfl.load_schedules(seasons)
    pbp = nfl.load_pbp(seasons)

    schedule_path = args.output_dir / "schedules.parquet"
    pbp_path = args.output_dir / "play_by_play.parquet"
    schedules.write_parquet(schedule_path)
    pbp.write_parquet(pbp_path)

    print("\nDownload summary")
    print("----------------")
    print(f"Schedule rows: {schedules.height:,}")
    print(f"Play-by-play rows: {pbp.height:,}")
    print(f"Schedule columns: {schedules.columns}")
    print(f"Play-by-play columns: {pbp.columns}")

    if "game_id" in schedules.columns and "game_id" in pbp.columns:
        schedule_ids = set(schedules.get_column("game_id").drop_nulls().to_list())
        pbp_ids = set(pbp.get_column("game_id").drop_nulls().to_list())
        missing = sorted(schedule_ids - pbp_ids)
        unexpected = sorted(pbp_ids - schedule_ids)
        print(f"Games in schedule: {len(schedule_ids):,}")
        print(f"Games represented in play-by-play: {len(pbp_ids):,}")
        print(f"Scheduled games without play-by-play: {len(missing):,}")
        if missing:
            print(f"First missing game IDs: {missing[:10]}")
        if unexpected:
            print(f"Play-by-play IDs absent from schedule: {unexpected[:10]}")
    else:
        print("WARNING: game_id is missing from one or both tables; ID coverage check skipped.")

    print(f"\nSaved schedules to: {schedule_path}")
    print(f"Saved play-by-play to: {pbp_path}")
    print("Raw data is local and gitignored; do not commit the Parquet files.")


if __name__ == "__main__":
    main()
