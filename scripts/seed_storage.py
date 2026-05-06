"""LocalStorage 통합 테스트용 더미 데이터 생성 스크립트.

DownloaderModule.playable_list_request 가 조회하는 레이아웃에 맞춰 빈 timestamp
파일을 만든다.

레이아웃:
    {root}/{prefix}/{vehicle_id}/{category}/{sensor_id_lower}/{yyyyMMdd}/{HH}/{MI}/seed_{ts}.bin

사용법:
    # 기본값 (conf/application.conf 의 STORAGE.ROOT/PREFIX 사용, 모든 19개 센서, 1분 분량)
    uv run python scripts/seed_storage.py

    # 커스텀
    uv run python scripts/seed_storage.py \\
        --vehicle-id vehicle-001 \\
        --sensors AT128_ROOF_FRONT,GNSS \\
        --start 20240101120000 \\
        --end 20240101120300 \\
        --interval-sec 1

    # 정리
    uv run python scripts/seed_storage.py --clean
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from config.project_config import ProjectConfig  # noqa: E402
from sensor_category.sensor_category import SensorCategory  # noqa: E402

TIME_FORMAT = "%Y%m%d%H%M%S"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=None, help="Storage root (default: conf STORAGE.ROOT)")
    parser.add_argument("--prefix", default=None, help="Storage prefix (default: conf STORAGE.PREFIX)")
    parser.add_argument("--vehicle-id", default="vehicle-001", help="vehicle_id (default: vehicle-001)")
    parser.add_argument(
        "--sensors",
        default="ALL",
        help="Comma-separated sensor IDs (default: ALL = 모든 19개 센서)",
    )
    parser.add_argument("--start", default="20240101120000", help="Start timestamp YYYYMMDDHHMMSS")
    parser.add_argument("--end", default="20240101120100", help="End timestamp YYYYMMDDHHMMSS")
    parser.add_argument("--interval-sec", type=int, default=1, help="File interval in seconds")
    parser.add_argument("--clean", action="store_true", help="Remove vehicle directory before seeding")
    return parser.parse_args()


def resolve_storage_root_prefix(cli_root: str | None, cli_prefix: str | None) -> tuple[str, str]:
    if cli_root is not None and cli_prefix is not None:
        return cli_root, cli_prefix
    ProjectConfig.set_config(str(REPO_ROOT / "conf/application.conf"))
    cfg = ProjectConfig.instance()
    return (cli_root or cfg.storage_root, cli_prefix or (cfg.storage_prefix or ""))


def resolve_sensors(arg: str) -> list[str]:
    if arg.upper() == "ALL":
        return SensorCategory.all_sensor_ids()
    sensors = [s.strip() for s in arg.split(",") if s.strip()]
    unknown = [s for s in sensors if not SensorCategory.has(s)]
    if unknown:
        raise SystemExit(f"Unknown sensor(s): {unknown}. Valid: {SensorCategory.all_sensor_ids()}")
    return sensors


def iter_timestamps(start: str, end: str, interval_sec: int):
    cur = datetime.strptime(start, TIME_FORMAT)
    last = datetime.strptime(end, TIME_FORMAT)
    while cur <= last:
        yield cur
        cur += timedelta(seconds=interval_sec)


def build_file_path(root: Path, prefix: str, vehicle_id: str, sensor_id: str, when: datetime) -> Path:
    category = SensorCategory.get(sensor_id)
    if category is None:
        raise ValueError(f"Unknown sensor_id: {sensor_id}")
    return (
        root
        / prefix
        / vehicle_id
        / category
        / sensor_id.lower()
        / when.strftime("%Y%m%d")
        / when.strftime("%H")
        / when.strftime("%M")
        / f"seed_{when.strftime(TIME_FORMAT)}.bin"
    )


def main() -> int:
    args = parse_args()
    root_str, prefix = resolve_storage_root_prefix(args.root, args.prefix)
    root = Path(root_str)
    sensors = resolve_sensors(args.sensors)

    vehicle_dir = root / prefix / args.vehicle_id

    if args.clean:
        if vehicle_dir.exists():
            shutil.rmtree(vehicle_dir)
            print(f"[clean] removed {vehicle_dir}")
        else:
            print(f"[clean] {vehicle_dir} does not exist")
        return 0

    print(f"[seed] root={root} prefix={prefix} vehicle={args.vehicle_id}")
    print(f"[seed] sensors={sensors}")
    print(f"[seed] range=[{args.start} .. {args.end}] interval={args.interval_sec}s")

    total = 0
    for sensor_id in sensors:
        count = 0
        for when in iter_timestamps(args.start, args.end, args.interval_sec):
            path = build_file_path(root, prefix, args.vehicle_id, sensor_id, when)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            count += 1
        total += count
        print(f"  - {sensor_id}: {count} files")

    print(f"[seed] done. total={total} files under {vehicle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
