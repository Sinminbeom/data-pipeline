"""BRIDGE 직렬화 + cache 본체 e2e 검증.

phase 2 (#84): Downloader가 source raw → cache로 복사
phase 3 (#86): Streamer가 cache에서 read
phase 4 (#88): BRIDGE 직렬화 — Downloader 완료 후 Streamer 트리거

PD_PLAY_REP OK 시점에 Downloader는 이미 cache 채움이 끝났음을 보장한다
(BRIDGE가 Downloader PLAY_REP 받은 뒤에야 Streamer를 트리거하기 때문).
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path

import socketio

from sensor_category.sensor_category import SensorCategory


_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
_SERVER_URL = "http://localhost:9999"


def _cache_pcap_path(env, sensor_id: str, when: datetime) -> Path:
    category = SensorCategory.get(sensor_id)
    assert category is not None, f"unknown sensor: {sensor_id}"
    sensor_lower = sensor_id.lower()
    ts = when.strftime(_TIMESTAMP_FORMAT)
    parts = [
        env.cache_prefix, env.vehicle_id, category, sensor_lower,
        when.strftime("%Y%m%d"), when.strftime("%H"), when.strftime("%M"),
        f"{sensor_lower}_{ts}.pcap",
    ]
    suffix = "/".join(p for p in parts if p)
    return env.cache_root / suffix


def test_play_populates_cache(fake_pcaps):
    """PD_PLAY_REP OK 후 cache 디렉토리에 chosen section 범위의 PCAP가 있어야 한다."""
    sio = socketio.Client()
    state: dict = {"playable_list": None, "play": None}
    list_event = threading.Event()
    play_event = threading.Event()

    def on_message(data):
        parsed = json.loads(data) if isinstance(data, str) else data
        pid = parsed.get("protocol_id")
        if pid == "PD_101":
            state["playable_list"] = parsed
            list_event.set()
        elif pid == "PD_201":
            state["play"] = parsed
            play_event.set()

    sio.on("message", on_message)
    sio.connect(_SERVER_URL, wait_timeout=10)

    try:
        list_req = {
            "protocol_id": "PD_100",
            "message_direction": 0, "sender": "UI", "receiver": "REST_SERVER",
            "vehicle_id": fake_pcaps.vehicle_id,
            "sensor_id_list": fake_pcaps.sensor_id_list,
            "start_time": fake_pcaps.start_time,
            "end_time": fake_pcaps.end_time,
        }
        sio.emit("message", json.dumps(list_req))
        assert list_event.wait(timeout=15), "PD_PLAYABLE_LIST_REP 응답을 시간 내 받지 못함"
        list_rep = state["playable_list"]
        assert list_rep is not None and list_rep["protocol_id"] == "PD_101"

        sections = list_rep.get("section_list") or []
        sensors = list_rep.get("sensor_id_list") or []
        assert sections, "재생 가능한 section이 없음"
        chosen = sections[0]

        play_req = {
            "protocol_id": "PD_200",
            "message_direction": 0, "sender": "UI", "receiver": "REST_SERVER",
            "section_id": chosen["sectionId"],
            "vehicle_id": fake_pcaps.vehicle_id,
            "sensor_id_list": sensors,
            "start_time": chosen["startTime"],
            "end_time": chosen["endTime"],
        }
        sio.emit("message", json.dumps(play_req))
        assert play_event.wait(timeout=30), "PD_PLAY_REP 응답을 시간 내 받지 못함"
        play_rep = state["play"]
        assert play_rep is not None and play_rep["protocol_id"] == "PD_201"
        assert play_rep.get("code") == "OK", f"play_rep not OK: {play_rep}"
    finally:
        sio.disconnect()

    # PD_PLAY_REP OK 도착 시점 = BRIDGE가 Streamer까지 완료한 시점.
    # Downloader는 그 직전에 완료했으므로 cache는 chosen section 범위만큼 채워져 있어야 한다.
    start_dt = datetime.strptime(chosen["startTime"], _TIMESTAMP_FORMAT)
    end_dt = datetime.strptime(chosen["endTime"], _TIMESTAMP_FORMAT)

    missing: list[Path] = []
    verified: int = 0
    cursor = start_dt
    while cursor <= end_dt:
        for sensor_id in fake_pcaps.sensor_id_list:
            cache_path = _cache_pcap_path(fake_pcaps, sensor_id, cursor)
            if not cache_path.exists():
                missing.append(cache_path)
            else:
                verified += 1
        cursor += timedelta(seconds=1)

    assert not missing, f"cache 누락 파일: {missing}"
    print(f"[client] cache 검증 완료 — {verified} files 존재")
