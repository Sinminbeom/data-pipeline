#!/bin/bash
# 다중 sensor 수신 검증용 — compositor로 10개 영상을 단일 창에 5x2 그리드로 합성.
# AM20 카메라 10개의 송출 port(5001~5010)을 각각 listen + 한 창에 타일 합성.
#
# 사용:
#   bash scripts/receive_multi_sensor.sh                     # 기본 (ximagesink, 5x2 합성)
#   bash scripts/receive_multi_sensor.sh fakesink            # 영상 없이 packet count만 (10개 별도 인스턴스)
#
# 환경변수 (영상 모드만):
#   COLS=5 ROWS=2          그리드 차원
#   TILE_W=480 TILE_H=270  각 타일 크기
#
# 종료: Ctrl+C — 일괄 종료
#
# 참고: WSLg는 EWMH _NET_CLIENT_LIST를 제공하지 않아 wmctrl/xdotool로 외부 창 배치 불가.
#       그래서 compositor로 GStreamer 내부에서 합성한다.

SINK="${1:-ximagesink}"
PORTS=(5001 5002 5003 5004 5005 5006 5007 5008 5009 5010)

export DISPLAY="${DISPLAY:-:0}"
COLS="${COLS:-5}"
ROWS="${ROWS:-2}"
TILE_W="${TILE_W:-480}"
TILE_H="${TILE_H:-270}"

PIDS=()

cleanup() {
    echo ""
    echo "[receiver] cleaning up ${#PIDS[@]} GStreamer process(es)..."
    kill "${PIDS[@]}" 2>/dev/null
    wait "${PIDS[@]}" 2>/dev/null
    echo "[receiver] done"
}
trap cleanup EXIT INT TERM

if [ "$SINK" = "fakesink" ]; then
    echo "[receiver] launching ${#PORTS[@]} GStreamer instances (sink=fakesink)"
    for port in "${PORTS[@]}"; do
        gst-launch-1.0 udpsrc port=$port buffer-size=2097152 ! \
          queue ! tsdemux ! \
          h264parse ! avdec_h264 ! videoconvert ! \
          fakesink sync=false \
          > /tmp/recv_${port}.log 2>&1 &
        PIDS+=($!)
        echo "  port=$port  pid=$!"
    done
else
    # compositor 단일 파이프라인 — sink pad마다 xpos/ypos/width/height 지정.
    # background=black, latency=0으로 일부 sink만 도착해도 즉시 표시.
    CMD="gst-launch-1.0 compositor name=mix background=black latency=0"
    for i in "${!PORTS[@]}"; do
        col=$((i % COLS))
        row=$((i / COLS))
        x=$((col * TILE_W))
        y=$((row * TILE_H))
        CMD="$CMD sink_${i}::xpos=${x} sink_${i}::ypos=${y} sink_${i}::width=${TILE_W} sink_${i}::height=${TILE_H}"
    done
    CMD="$CMD ! videoconvert ! ${SINK} sync=false"
    for i in "${!PORTS[@]}"; do
        port="${PORTS[$i]}"
        CMD="$CMD udpsrc port=${port} buffer-size=2097152 ! queue ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! videoscale ! video/x-raw,width=${TILE_W},height=${TILE_H} ! mix.sink_${i}"
    done
    echo "[receiver] launching compositor (sink=$SINK, ${ROWS}x${COLS} grid, tile=${TILE_W}x${TILE_H})"
    for i in "${!PORTS[@]}"; do
        col=$((i % COLS))
        row=$((i / COLS))
        echo "  sink_${i}: port=${PORTS[$i]} pos=(${col},${row}) → (${TILE_W}x${TILE_H})"
    done
    eval "$CMD > /tmp/recv_compositor.log 2>&1 &"
    PIDS+=($!)
fi

echo ""
echo "[receiver] running. Press Ctrl+C to stop."
if [ "$SINK" = "fakesink" ]; then
    echo "[receiver] log per port: /tmp/recv_<port>.log"
else
    echo "[receiver] log: /tmp/recv_compositor.log"
fi

wait
