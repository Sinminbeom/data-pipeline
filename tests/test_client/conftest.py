"""test_client e2e 테스트용 공통 fixture.

- 4개 앱(REST_SERVER, MESSAGE_BRIDGE, DOWNLOADER, STREAMER) 실행 전제.
- fake PCAP 파일을 임시 vehicle 경로에 생성 — playable_list lookup과 streamer
  pcap reader 모두 만족하도록 ``{sensor_lower}_{timestamp}.pcap`` 규약 사용.
"""
from __future__ import annotations

import shutil
import struct
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from config.project_config import ProjectConfig  # noqa: E402
from sensor_category.sensor_category import SensorCategory  # noqa: E402

_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

# 테스트용 unique vehicle — 기존 seed(vehicle-001)와 격리.
_TEST_VEHICLE_ID = "vehicle-test-lifecycle"
_TEST_SENSORS = ["AT128_ROOF_FRONT", "GNSS"]
_TEST_START = "20240101120000"
# 4초 분량 — seek가 중간 시각으로 이동 가능하도록 여유.
_TEST_END = "20240101120004"


@dataclass(frozen=True)
class FakePcapEnv:
    vehicle_id: str
    sensor_id_list: list[str]
    start_time: str
    end_time: str


def _minimal_udp_ethernet_packet() -> bytes:
    """Ethernet UDP 최소 패킷 — 42 byte payload (link 14 + IP 20 + UDP 8)."""
    eth = bytes(12) + b"\x08\x00"           # dst+src MAC zeros, ethertype IPv4
    ip = (
        b"\x45\x00\x00\x1c"                  # ver/ihl, dscp, total_len=28
        b"\x00\x00\x00\x00"                  # id, flags+offset
        b"\x40\x11\x00\x00"                  # ttl=64, protocol=17 (UDP), checksum=0
        b"\x7f\x00\x00\x01"                  # src=127.0.0.1
        b"\x7f\x00\x00\x01"                  # dst=127.0.0.1
    )
    udp = b"\x04\xd2\x04\xd2\x00\x08\x00\x00"  # src=dst=1234, len=8, checksum=0
    return eth + ip + udp


def _write_minimal_pcap(path: Path, when: datetime) -> None:
    """PCAP 1 packet — file header(24) + packet header(16) + body(42)."""
    body = _minimal_udp_ethernet_packet()
    file_header = struct.pack(
        "<IHHIIII",
        0xA1B2C3D4,          # magic
        2, 4,                # major, minor
        0, 0,                # gmt_to_local, timestamp(unused)
        65535,               # max_caplen
        1,                   # link_type = Ethernet
    )
    packet_header = struct.pack(
        "<IIII",
        int(when.timestamp()),
        0,                   # microseconds
        len(body),
        len(body),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(file_header)
        f.write(packet_header)
        f.write(body)


def _build_pcap_path(root: Path, prefix: str, sensor_id: str, when: datetime) -> Path:
    category = SensorCategory.get(sensor_id)
    if category is None:
        raise ValueError(f"unknown sensor: {sensor_id}")
    sensor_lower = sensor_id.lower()
    timestamp = when.strftime(_TIMESTAMP_FORMAT)
    parts = [prefix, _TEST_VEHICLE_ID, category, sensor_lower,
             when.strftime("%Y%m%d"), when.strftime("%H"), when.strftime("%M"),
             f"{sensor_lower}_{timestamp}.pcap"]
    return root.joinpath(*[p for p in parts if p])


@pytest.fixture(scope="session")
def fake_pcaps() -> Iterator[FakePcapEnv]:
    """fake PCAP 파일 set up + 세션 종료 시 cleanup."""
    ProjectConfig.set_config(str(REPO_ROOT / "conf/application.conf"))
    cfg = ProjectConfig.instance()
    root = Path(cfg.storage_root)
    prefix = cfg.storage_prefix or ""

    vehicle_dir = root / prefix / _TEST_VEHICLE_ID

    start_dt = datetime.strptime(_TEST_START, _TIMESTAMP_FORMAT)
    end_dt = datetime.strptime(_TEST_END, _TIMESTAMP_FORMAT)

    cursor = start_dt
    while cursor <= end_dt:
        for sensor_id in _TEST_SENSORS:
            _write_minimal_pcap(_build_pcap_path(root, prefix, sensor_id, cursor), cursor)
        cursor += timedelta(seconds=1)

    try:
        yield FakePcapEnv(
            vehicle_id=_TEST_VEHICLE_ID,
            sensor_id_list=list(_TEST_SENSORS),
            start_time=_TEST_START,
            end_time=_TEST_END,
        )
    finally:
        if vehicle_dir.exists():
            shutil.rmtree(vehicle_dir, ignore_errors=True)
