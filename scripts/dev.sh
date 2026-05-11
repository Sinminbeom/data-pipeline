#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

# 백그라운드로 4개 서버 실행
uv run python src/rest_server_app.py &
PID_REST_SERVER=$!
uv run python src/message_bridge_app.py &
PID_MESSAGE_BRIDGE=$!
uv run python src/downloader_app.py &
PID_DOWNLOADER=$!
uv run python src/streamer_app.py &
PID_STREAMER=$!

# 종료 시 정리
trap "kill $PID_REST_SERVER $PID_MESSAGE_BRIDGE $PID_DOWNLOADER $PID_STREAMER 2>/dev/null || true" EXIT

# 서버 startup 대기
sleep 2

# 테스트 실행
uv run pytest tests/test_client/test_playable_list.py -s
uv run pytest tests/test_client/test_play.py -s
uv run pytest tests/test_client/test_pause.py -s
uv run pytest tests/test_client/test_seek.py -s
uv run pytest tests/test_client/test_close.py -s
uv run pytest tests/test_client/test_stop.py -s