import json
import threading

import socketio


def test_playable_list():
    """REST_SERVER로 PD_PLAYABLE_LIST_REQ를 보내고 PD_PLAYABLE_LIST_REP를 수신.

    full flow:
        client → REST_SERVER → MESSAGE_BRIDGE → DOWNLOADER (lookup) → 매니저 모음
              ← REST_SERVER ← MESSAGE_BRIDGE ← DOWNLOADER (PLAYABLE_LIST_REP)
    """
    sio = socketio.Client()
    received: dict = {}
    response_event = threading.Event()

    @sio.event
    def connect():
        print("[client] connected")

    @sio.event
    def disconnect():
        print("[client] disconnected")

    def on_message(data):
        print(f"[client] recv: {data}")
        parsed = json.loads(data) if isinstance(data, str) else data
        if parsed.get("protocol_id") == "PD_101":
            received.update(parsed)
            response_event.set()

    sio.on("message", on_message)

    sio.connect("http://localhost:9999", wait_timeout=10)

    request = {
        "protocol_id": "PD_100",
        "message_direction": 0,
        "sender": "UI",
        "receiver": "REST_SERVER",
        "vehicle_id": "vehicle-001",
        "sensor_id_list": ["AT128_ROOF_FRONT", "GNSS"],
        "start_time": "20240101120000",
        "end_time": "20240101120100",
    }
    sio.emit("message", json.dumps(request))
    print(f"[client] sent: {request}")

    got = response_event.wait(timeout=15)
    sio.disconnect()

    assert got, "PD_PLAYABLE_LIST_REP 응답을 시간 내 받지 못함"
    assert received["protocol_id"] == "PD_101"
    print(f"[client] code={received.get('code')} sensors={received.get('sensor_id_list')}")
    print(f"[client] sections={received.get('section_list')}")
