"""UDP rate 측정 helper — lifecycle 명령 후 실제 UDP 송출 동작을 관찰한다.

PcapSenderThread는 STREAM_OUTPUT config에 명시된 IP/PORT로 UDP packet을 송출.
테스트는 그 IP/PORT를 bind해 들어오는 packet 수를 셈으로써 송출이 멈췄는지/
계속되는지를 직접 검증한다.

전제: STREAM_OUTPUT IP가 127.0.0.1(또는 localhost) 이어야 함. 아니면 skip.
"""
from __future__ import annotations

import json
import socket
import threading
import time
from contextlib import contextmanager
from typing import Iterator

import pytest
import socketio

_LOCALHOST_IPS = frozenset(["127.0.0.1", "localhost", "0.0.0.0"])
_SERVER_URL = "http://localhost:9999"


class UdpRateMonitor:
    """UDP socket bound listener — background thread에서 packet count 누적.

    `with UdpRateMonitor(ip, port) as m:` 또는 start()/stop() 수동 사용.
    """

    def __init__(self, ip: str, port: int) -> None:
        self._ip = ip
        self._port = port
        self._socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._count = 0
        self._lock = threading.Lock()

    def start(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(0.1)
        self._socket.bind((self._ip, self._port))
        self._stop.clear()
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1)
            self._thread = None
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def reset_count(self) -> None:
        with self._lock:
            self._count = 0

    def get_count(self) -> int:
        with self._lock:
            return self._count

    def count_in_window(self, duration_seconds: float) -> int:
        """count를 0으로 reset 후 duration만큼 sleep, 그 사이 도착 packet 수 반환."""
        self.reset_count()
        time.sleep(duration_seconds)
        return self.get_count()

    def _recv_loop(self) -> None:
        assert self._socket is not None
        while not self._stop.is_set():
            try:
                _ = self._socket.recvfrom(65535)
                with self._lock:
                    self._count += 1
            except socket.timeout:
                continue
            except OSError:
                break

    def __enter__(self) -> "UdpRateMonitor":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()


@contextmanager
def udp_monitor(ip: str, port: int) -> Iterator[UdpRateMonitor]:
    monitor = UdpRateMonitor(ip, port)
    monitor.start()
    try:
        yield monitor
    finally:
        monitor.stop()


def maybe_skip_if_not_localhost(ip: str) -> None:
    """STREAM_OUTPUT IP가 localhost 계열이 아니면 테스트 skip."""
    if ip not in _LOCALHOST_IPS:
        pytest.skip(f"STREAM_OUTPUT IP={ip}는 localhost가 아님 — UDP 검증 skip")


def get_first_sensor_stream_output(fake_pcaps) -> tuple[str, int, str]:
    """fake_pcaps의 첫 sensor의 STREAM_OUTPUT (ip, port, sensor_id) 반환."""
    from config.project_config import ProjectConfig

    sensor_id = fake_pcaps.sensor_id_list[0]
    cfg = ProjectConfig.instance()
    ip, port = cfg.get_stream_output(sensor_id)
    return ip, port, sensor_id


def validate_lifecycle_stops_udp(
    fake_pcaps,
    *,
    lifecycle_req_id: str,
    lifecycle_rep_id: str,
    extra_lifecycle_payload: dict | None = None,
) -> None:
    """공통 시나리오: Play → rate>0 확인 → lifecycle 명령 → rate=0 확인.

    pause/stop/close가 모두 UDP 송출을 멈추는 의미라 같은 helper로 처리.
    """
    ip, port, sensor_id = get_first_sensor_stream_output(fake_pcaps)
    maybe_skip_if_not_localhost(ip)

    sio = socketio.Client()
    state: dict = {"playable_list": None, "play": None, "lifecycle": None}
    list_event = threading.Event()
    play_event = threading.Event()
    lifecycle_event = threading.Event()

    def on_message(data):
        parsed = json.loads(data) if isinstance(data, str) else data
        pid = parsed.get("protocol_id")
        if pid == "PD_101":
            state["playable_list"] = parsed
            list_event.set()
        elif pid == "PD_201":
            state["play"] = parsed
            play_event.set()
        elif pid == lifecycle_rep_id:
            state["lifecycle"] = parsed
            lifecycle_event.set()

    sio.on("message", on_message)
    sio.connect(_SERVER_URL, wait_timeout=10)

    with udp_monitor(ip, port) as monitor:
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
            assert list_event.wait(timeout=15), "PD_PLAYABLE_LIST_REP timeout"
            list_rep = state["playable_list"]
            sections = list_rep.get("section_list") or []
            sensors = list_rep.get("sensor_id_list") or []
            assert sections, "재생 가능 section 없음"
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
            assert play_event.wait(timeout=30), "PD_PLAY_REP timeout"
            assert state["play"].get("code") == "OK", state["play"]

            # PD_PLAY_REP OK = reader 버퍼 threshold 도달, sender 송출 시작.
            # 3초 window — 1packet/s rate라 최소 1개 이상은 도착해야 함.
            during_play = monitor.count_in_window(3.0)
            assert during_play > 0, (
                f"Play 중인데 UDP packet이 도착하지 않음 ({sensor_id}@{ip}:{port} count={during_play})"
            )

            lifecycle_req = {
                "protocol_id": lifecycle_req_id,
                "message_direction": 0, "sender": "UI", "receiver": "REST_SERVER",
            }
            if extra_lifecycle_payload:
                lifecycle_req.update(extra_lifecycle_payload)
            sio.emit("message", json.dumps(lifecycle_req))
            assert lifecycle_event.wait(timeout=15), f"{lifecycle_rep_id} timeout"
            assert state["lifecycle"].get("code") == "OK", state["lifecycle"]

            # lifecycle OK 후 sender가 송출을 멈췄어야 함. 2초 window에서 0이어야 한다.
            after_lifecycle = monitor.count_in_window(2.0)
            assert after_lifecycle == 0, (
                f"{lifecycle_req_id} 후에도 UDP packet 도착 ({sensor_id}@{ip}:{port} count={after_lifecycle})"
            )
        finally:
            sio.disconnect()
