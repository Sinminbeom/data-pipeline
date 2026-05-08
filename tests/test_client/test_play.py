import json
import threading

import socketio


def test_playable_list_then_play():
    """PlayableList → 응답에서 section 골라 Play 연속 시나리오.

    full flow:
        1) client → REST_SERVER → MESSAGE_BRIDGE → DOWNLOADER (lookup)
                 ← REST_SERVER ← MESSAGE_BRIDGE ← DOWNLOADER (PD_PLAYABLE_LIST_REP)
        2) client → REST_SERVER → STREAMER Manager (PLAY state) → STREAMER modules (placeholder OK)
                 ← REST_SERVER ← MESSAGE_BRIDGE ← STREAMER Manager (PD_PLAY_REP via group_response)

    참고:
      - PLAY_REQ는 BRIDGE+STREAMER+DOWNLOADER 3 receivers broadcast.
      - DOWNLOADER 쪽 handle_play_request은 NotImplementedError지만
        listener catch 후 STREAMER 흐름은 독립 진행.
      - StreamerModule.PlayState는 placeholder(즉시 OK 응답 후 WAIT 복귀).
    """
    sio = socketio.Client()
    state: dict = {"playable_list": None, "play": None}
    list_event = threading.Event()
    play_event = threading.Event()

    @sio.event
    def connect():
        print("[client] connected")

    @sio.event
    def disconnect():
        print("[client] disconnected")

    def on_message(data):
        print(f"[client] recv: {data}")
        parsed = json.loads(data) if isinstance(data, str) else data
        pid = parsed.get("protocol_id")
        if pid == "PD_101":
            state["playable_list"] = parsed
            list_event.set()
        elif pid == "PD_201":
            state["play"] = parsed
            play_event.set()

    sio.on("message", on_message)
    sio.connect("http://localhost:9999", wait_timeout=10)

    # 1) PlayableList 요청
    list_request = {
        "protocol_id": "PD_100",
        "message_direction": 0,
        "sender": "UI",
        "receiver": "REST_SERVER",
        "vehicle_id": "vehicle-001",
        "sensor_id_list": ["AT128_ROOF_FRONT", "GNSS"],
        "start_time": "20240101120000",
        "end_time": "20240101120100",
    }
    sio.emit("message", json.dumps(list_request))
    print(f"[client] sent: {list_request}")

    got_list = list_event.wait(timeout=15)
    assert got_list, "PD_PLAYABLE_LIST_REP 응답을 시간 내 받지 못함"
    assert state["playable_list"]["protocol_id"] == "PD_101"

    sections = state["playable_list"].get("section_list") or []
    sensors = state["playable_list"].get("sensor_id_list") or []
    assert sections, "재생 가능한 section이 없음 — Play 단계 진행 불가"
    chosen = sections[0]
    print(f"[client] chosen section: {chosen}")

    # 2) 응답에서 받은 첫 section을 토대로 Play 요청
    play_request = {
        "protocol_id": "PD_200",
        "message_direction": 0,
        "sender": "UI",
        "receiver": "REST_SERVER",
        "section_id": chosen["sectionId"],
        "vehicle_id": "vehicle-001",
        "sensor_id_list": sensors,
        "start_time": chosen["startTime"],
        "end_time": chosen["endTime"],
    }
    sio.emit("message", json.dumps(play_request))
    print(f"[client] sent: {play_request}")

    got_play = play_event.wait(timeout=15)
    sio.disconnect()

    assert got_play, "PD_PLAY_REP 응답을 시간 내 받지 못함"
    assert state["play"]["protocol_id"] == "PD_201"
    print(f"[client] play code={state['play'].get('code')} reason={state['play'].get('reason')}")
