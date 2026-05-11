"""Pause/Seek/Close/Stop e2e 테스트 공통 helper.

test_play.py의 PlayableList → Play 시퀀스를 그대로 재사용하고, 그 위에서 한
종류의 라이프사이클 명령(Pause/Seek/Close/Stop)을 송수신·검증한다.
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from typing import Any, Callable, Optional

import socketio

_SERVER_URL = "http://localhost:9999"
_CONNECT_TIMEOUT = 10
_LIST_TIMEOUT = 15
_PLAY_TIMEOUT = 15
_LIFECYCLE_TIMEOUT = 15

_PD_PLAYABLE_LIST_REQ = "PD_100"
_PD_PLAYABLE_LIST_REP = "PD_101"
_PD_PLAY_REQ = "PD_200"
_PD_PLAY_REP = "PD_201"


@dataclass
class _SessionState:
    list_rep: dict
    play_rep: dict
    lifecycle_rep: dict


def _build_list_request(vehicle_id: str, sensors: list[str], start: str, end: str) -> dict:
    return {
        "protocol_id": _PD_PLAYABLE_LIST_REQ,
        "message_direction": 0,
        "sender": "UI",
        "receiver": "REST_SERVER",
        "vehicle_id": vehicle_id,
        "sensor_id_list": sensors,
        "start_time": start,
        "end_time": end,
    }


def _build_play_request(section: dict, vehicle_id: str, sensors: list[str]) -> dict:
    return {
        "protocol_id": _PD_PLAY_REQ,
        "message_direction": 0,
        "sender": "UI",
        "receiver": "REST_SERVER",
        "section_id": section["sectionId"],
        "vehicle_id": vehicle_id,
        "sensor_id_list": sensors,
        "start_time": section["startTime"],
        "end_time": section["endTime"],
    }


def run_lifecycle_scenario(
    *,
    vehicle_id: str,
    sensor_id_list: list[str],
    start_time: str,
    end_time: str,
    lifecycle_req_id: str,
    lifecycle_rep_id: str,
    extra_payload: Optional[dict] = None,
    on_section: Optional[Callable[[dict], None]] = None,
) -> _SessionState:
    """PlayableList → Play → 라이프사이클 한 종 시나리오를 실행하고 응답을 모은다.

    extra_payload: 라이프사이클 요청에 합쳐질 추가 필드 (Seek의 start_time 등).
    on_section: PlayableList 응답에서 chosen section을 받아 추가 검증 hook (필요 시).
    """
    sio = socketio.Client()
    list_event = threading.Event()
    play_event = threading.Event()
    lifecycle_event = threading.Event()
    state: dict[str, Optional[dict[str, Any]]] = {
        "playable_list": None,
        "play": None,
        "lifecycle": None,
    }

    @sio.event
    def connect():  # type: ignore[no-redef]
        print("[client] connected")

    @sio.event
    def disconnect():  # type: ignore[no-redef]
        print("[client] disconnected")

    def on_message(data):
        print(f"[client] recv: {data}")
        parsed = json.loads(data) if isinstance(data, str) else data
        pid = parsed.get("protocol_id")
        if pid == _PD_PLAYABLE_LIST_REP:
            state["playable_list"] = parsed
            list_event.set()
        elif pid == _PD_PLAY_REP:
            state["play"] = parsed
            play_event.set()
        elif pid == lifecycle_rep_id:
            state["lifecycle"] = parsed
            lifecycle_event.set()

    sio.on("message", on_message)
    sio.connect(_SERVER_URL, wait_timeout=_CONNECT_TIMEOUT)

    try:
        list_req = _build_list_request(vehicle_id, sensor_id_list, start_time, end_time)
        sio.emit("message", json.dumps(list_req))
        print(f"[client] sent: {list_req}")
        assert list_event.wait(timeout=_LIST_TIMEOUT), "PD_PLAYABLE_LIST_REP 응답을 시간 내 받지 못함"
        list_rep = state["playable_list"]
        assert list_rep is not None and list_rep["protocol_id"] == _PD_PLAYABLE_LIST_REP

        sections = list_rep.get("section_list") or []
        assert sections, "재생 가능한 section이 없음 — Play 단계 진행 불가"
        chosen = sections[0]
        print(f"[client] chosen section: {chosen}")
        if on_section is not None:
            on_section(chosen)

        play_req = _build_play_request(chosen, vehicle_id, sensor_id_list)
        sio.emit("message", json.dumps(play_req))
        print(f"[client] sent: {play_req}")
        assert play_event.wait(timeout=_PLAY_TIMEOUT), "PD_PLAY_REP 응답을 시간 내 받지 못함"
        play_rep = state["play"]
        assert play_rep is not None and play_rep["protocol_id"] == _PD_PLAY_REP

        lifecycle_req = {
            "protocol_id": lifecycle_req_id,
            "message_direction": 0,
            "sender": "UI",
            "receiver": "REST_SERVER",
        }
        if extra_payload:
            lifecycle_req.update(extra_payload)
        sio.emit("message", json.dumps(lifecycle_req))
        print(f"[client] sent: {lifecycle_req}")
        assert lifecycle_event.wait(timeout=_LIFECYCLE_TIMEOUT), (
            f"{lifecycle_rep_id} 응답을 시간 내 받지 못함"
        )
        lifecycle_rep = state["lifecycle"]
        assert lifecycle_rep is not None
    finally:
        sio.disconnect()

    return _SessionState(
        list_rep=list_rep,
        play_rep=play_rep,
        lifecycle_rep=lifecycle_rep,
    )
