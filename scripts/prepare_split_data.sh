#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "사용법: $0 <STORAGE_ROOT>"
  echo "예: $0 /home/shinminbeom/infra_glue/personal/sensor-data-replayer/data"
  exit 1
fi

STORAGE_ROOT="$1"
VEHICLE="vehicle-001"
SENSOR="AM20_FRONT_CENTER_RIGHT_DOWN"
SENSOR_LOWER=$(echo "$SENSOR" | tr '[:upper:]' '[:lower:]')
CATEGORY="camera"
SRC_PCAP="$STORAGE_ROOT/fullpcap/full.pcap"

# 1) source 확인
if [ ! -f "$SRC_PCAP" ]; then
  echo "ERROR: $SRC_PCAP 가 없음"
  exit 1
fi

# 2) 캡처 시간 범위 추출
START_EPOCH=$(capinfos -aSe "$SRC_PCAP" 2>/dev/null | awk '/First packet time/ { gsub(/[^0-9.]/, "", $NF); split($NF, a, "."); print a[1] }')
END_EPOCH=$(  capinfos -aSe "$SRC_PCAP" 2>/dev/null | awk '/Last packet time/  { gsub(/[^0-9.]/, "", $NF); split($NF, a, "."); print a[1] }')

if [ -z "$START_EPOCH" ] || [ -z "$END_EPOCH" ]; then
  echo "ERROR: 시간 추출 실패"
  exit 1
fi

YYYYMMDD=$(date -d "@$START_EPOCH" "+%Y%m%d")
HHMMSS=$(  date -d "@$START_EPOCH" "+%H%M%S")
echo "캡처 시작: $YYYYMMDD $HHMMSS (epoch $START_EPOCH ~ $END_EPOCH)"

# 3) raw 배치 (data/raw/{vehicle}/{sensor}/{YYYYMMDD}/full_{HHMMSS}.pcap)
RAW_DIR="$STORAGE_ROOT/raw/$VEHICLE/$SENSOR_LOWER/$YYYYMMDD"
mkdir -p "$RAW_DIR"
cp "$SRC_PCAP" "$RAW_DIR/full_${HHMMSS}.pcap"
echo "raw 배치: $RAW_DIR/full_${HHMMSS}.pcap"

# 4) 정시 경계 1초 분할 → 임시 디렉토리
TMP_SPLIT="/tmp/split_$$"
mkdir -p "$TMP_SPLIT"
for ((s=START_EPOCH; s<=END_EPOCH; s++)); do
  ts=$(date -d "@$s" "+%Y%m%d%H%M%S")
  start_time=$(date -d "@$s"       "+%Y-%m-%d %H:%M:%S.000000")
  end_time=$(  date -d "@$((s+1))" "+%Y-%m-%d %H:%M:%S.000000")
  editcap -F pcap -A "$start_time" -B "$end_time" "$SRC_PCAP" "$TMP_SPLIT/temp_${ts}.pcap" 2>/dev/null
done

# 5) split 디렉토리 구조로 배치
SPLIT_BASE="$STORAGE_ROOT/split/$VEHICLE/$CATEGORY/$SENSOR_LOWER"
rm -rf "$SPLIT_BASE"
for f in "$TMP_SPLIT"/temp_*.pcap; do
  TS=$(basename "$f" | grep -oP '\d{14}')
  DEST_DIR="$SPLIT_BASE/${TS:0:8}/${TS:8:2}/${TS:10:2}"
  mkdir -p "$DEST_DIR"
  cp "$f" "$DEST_DIR/${SENSOR_LOWER}_${TS}.pcap"
done
rm -rf "$TMP_SPLIT"

# 6) 결과 출력
echo ""
echo "=== raw ==="
find "$STORAGE_ROOT/raw" -type f -name "*.pcap" | sort
echo ""
echo "=== split ==="
find "$STORAGE_ROOT/split" -type f -name "*.pcap" | sort
