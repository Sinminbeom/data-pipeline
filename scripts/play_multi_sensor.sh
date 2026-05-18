#!/bin/bash
# 다중 sensor 동시 PLAY 검증용 스크립트.
# AM20 카메라 10개에 동시 PLAY 보내고 자연 EOF까지 송출 흐름을 확인.
#
# 사용:
#   bash scripts/play_multi_sensor.sh                              # 기본값
#   bash scripts/play_multi_sensor.sh <START_TIME> <END_TIME>
#
# 예시:
#   bash scripts/play_multi_sensor.sh 20260513115345 20260513115420

START_TIME_ARG="${1:-20260513115345}"
END_TIME_ARG="${2:-20260513115420}"

START_TIME="$START_TIME_ARG" END_TIME="$END_TIME_ARG" uv run python << 'EOF'
import os
import threading
import socketio
import json
import time

SENSORS = [
    "AM20_FRONT_CENTER_RIGHT_DOWN",
    "AM20_FRONT_RIGHT_REAR",
    "AM20_REAR_CENTER_RIGHT",
    "AM20_FRONT_LEFT_REAR",
    "AM20_REAR_RIGHT_EDGE",
    "AM20_LEFT_REAR_EDGE",
    "AM20_FRONT_CENTER_LEFT_UP",
    "AM20_FRONT_CENTER_RIGHT_UP",
    "AM20_FRONT_RIGHT_FRONT",
    "AM20_FRONT_LEFT_FRONT",
]

VEHICLE_ID = "VEHICLE-001"
START_TIME = os.environ["START_TIME"]
END_TIME = os.environ["END_TIME"]
LIST_TIMEOUT_SEC = 30
PLAY_DURATION_SEC = 35

list_event = threading.Event()
play_event = threading.Event()
sectionId = [None]   # mutable container

sio = socketio.Client()

@sio.event
def message(data):
    try:
        parsed = json.loads(data)
    except Exception:
        return
    pid = parsed.get("protocol_id")
    print(f"[client] recv: {pid} code={parsed.get('code', '-')}")
    if pid == "PD_101":
        sections = parsed.get("section_list") or []
        if sections:
            sectionId[0] = sections[0]["sectionId"]
        list_event.set()
    elif pid == "PD_201":
        play_event.set()

print(f"[client] START_TIME={START_TIME}, END_TIME={END_TIME}")
sio.connect("http://127.0.0.1:9999")

print(f"[client] sending PLAYABLE_LIST ({len(SENSORS)} sensors)")
sio.emit("message", json.dumps({
    "protocol_id": "PD_100",
    "message_direction": 0,
    "sender": "UI",
    "receiver": "REST_SERVER",
    "vehicle_id": VEHICLE_ID,
    "sensor_id_list": SENSORS,
    "start_time": START_TIME,
    "end_time": END_TIME,
}))

if not list_event.wait(timeout=LIST_TIMEOUT_SEC):
    print(f"[client] ERROR: PD_101 응답 {LIST_TIMEOUT_SEC}초 안에 못 받음")
    sio.disconnect()
    raise SystemExit(1)

print(f"[client] PD_101 OK (section {sectionId[0]}), sending PLAY")
sio.emit("message", json.dumps({
    "protocol_id": "PD_200",
    "message_direction": 0,
    "sender": "UI",
    "receiver": "REST_SERVER",
    "section_id": sectionId[0],
    "vehicle_id": VEHICLE_ID,
    "sensor_id_list": SENSORS,
    "start_time": START_TIME,
    "end_time": END_TIME,
}))

if not play_event.wait(timeout=LIST_TIMEOUT_SEC):
    print(f"[client] WARN: PD_201 응답 timeout (송출은 진행될 수 있음)")
else:
    print(f"[client] PD_201 OK")

print(f"[client] sleeping {PLAY_DURATION_SEC}s (no STOP — natural EOF)")
time.sleep(PLAY_DURATION_SEC)

sio.disconnect()
print("[client] done")
EOF
