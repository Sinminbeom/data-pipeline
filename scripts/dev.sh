#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

# 백그라운드로 3개 서버 실행
uv run python src/rest_server_app.py &
PID_REST=$!
uv run python src/message_bridge_app.py &
PID_MB=$!
uv run python src/downloader_app.py &
PID_DL=$!

# 종료 시 정리
trap "kill $PID_REST $PID_MB $PID_DL 2>/dev/null || true" EXIT

# 서버 startup 대기
sleep 2

# 테스트 실행
uv run pytest tests/test_client/test_client.py -s
