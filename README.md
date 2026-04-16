# data-pipeline

자율주행 차량의 멀티 센서 데이터(LiDAR, GNSS, Camera)를 수집·처리하는 분산 파이프라인 시스템.

## 개요

차량에 장착된 센서로부터 데이터를 수신하고, UI 클라이언트의 요청에 따라 센서 데이터를 다운로드·제공하는 파이프라인입니다. 3개의 독립 프로세스(`REST Server`, `Message Bridge`, `Downloader`)가 Redis pub/sub을 통해 통신합니다.

## 아키텍처

```
UI Client (Socket.IO)
        │
        ▼
  REST Server ──────────────────────────────────┐
  (FastAPI + Socket.IO, port 9999)              │
        │                                       │
        │ Redis pub/sub                         │
        ▼                                       │
 Message Bridge                                 │
        │                                       │
        │ Redis pub/sub                         │
        ▼                                       │
   Downloader Manager                           │
   ├── LiDAR Module × 8                         │
   ├── GNSS Module  × 1                         │
   └── Camera Module × 10                       │
        │                                       │
        └───────── 응답 ─────────────────────────┘
```

## 지원 센서

| 타입 | 모델 | 수량 |
|------|------|------|
| LiDAR (루프) | AT128 (Front / Right / Rear / Left) | 4 |
| LiDAR (범퍼) | RSBP (Front / Right / Rear / Left) | 4 |
| GNSS | GNSS | 1 |
| Camera | AM20 (10 방향) | 10 |

## 기술 스택

| 분류 | 기술 |
|------|------|
| 언어 | Python 3.11 |
| 패키지 관리 | uv |
| REST / WebSocket | FastAPI + python-socketio + uvicorn |
| IPC 브로커 | Redis 7 (pub/sub) |
| 직렬화 | jsonpickle |
| 린팅 / 포맷 | ruff |
| 타입 체크 | pyright |
| 테스트 | pytest |
| 공통 라이브러리 | oncx-core (내부) |

## 디렉터리 구조

```
data-pipeline/
├── conf/
│   ├── application_windows.conf   # 서비스 설정 (Redis, REST 바인딩 등)
│   └── logging.conf               # 로깅 설정
├── src/
│   ├── app/
│   │   ├── downloader/            # 다운로더 프로세스
│   │   ├── message_bridge/        # 메시지 브릿지 프로세스
│   │   └── rest/                  # REST / WebSocket 프로세스
│   ├── common/
│   │   ├── event_bus/             # Redis / 내부 큐 이벤트 버스
│   │   ├── process/               # 프로세스 베이스 클래스
│   │   └── state/                 # 상태 머신
│   ├── config/                    # 설정 로더
│   ├── define/                    # 통신 타입 Enum
│   ├── process_category/          # 프로세스 카테고리 레지스트리
│   ├── protocol/                  # 메시지 프로토콜 정의
│   ├── utils/                     # 공통 유틸리티
│   ├── rest_server_app.py         # REST 서버 진입점
│   ├── message_bridge_app.py      # 메시지 브릿지 진입점
│   └── downloader_app.py          # 다운로더 진입점
└── tests/
    ├── test_client/
    ├── test_process_category/
    └── test_state/
```

## 사전 요구사항

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 설치
- Redis 서버 실행 중 (기본: `localhost:6379`)

## 설치

```bash
# 저장소 클론
git clone git@github.com:Sinminbeom/data-pipeline.git
cd data-pipeline

# 의존성 설치
uv sync --dev
```

## 설정

`conf/application_windows.conf`를 환경에 맞게 수정합니다.

```ini
[COMMON]
ProjectName = data-pipeline
ChannelName = test        # Redis pub/sub 채널명

[IMDG]
ServerIp = 127.0.0.1      # Redis 호스트
ServerPort = 6379         # Redis 포트
PoolSize = 10

[REST]
BindIp = 0.0.0.0
BindPort = 9999           # WebSocket 서버 포트
```

## 실행

3개 프로세스를 각각 별도 터미널에서 실행합니다.

```bash
# 1. REST 서버
cd src && uv run python rest_server_app.py

# 2. 메시지 브릿지
cd src && uv run python message_bridge_app.py

# 3. 다운로더
cd src && uv run python downloader_app.py
```

## 개발

```bash
# 린팅 / 포맷
uv run ruff check . --fix
uv run ruff format .

# 타입 체크
uv run pyright

# 테스트
uv run pytest

# 커버리지
uv run pytest --cov=src --cov-report=term-missing
```

## 메시지 프로토콜

UI 클라이언트는 Socket.IO `message` 이벤트로 JSON 메시지를 전송합니다.

```json
{
  "protocol_id": "PLAYABLE_LIST_REQ",
  "receiver": "REST_SERVER",
  "vehicle_id": "vehicle-001",
  "sensor_id_list": ["AT128_ROOF_FRONT", "GNSS"],
  "start_time": "2024-01-01T00:00:00",
  "end_time": "2024-01-01T01:00:00"
}
```

| protocol_id | 설명 |
|---|---|
| `PLAYABLE_LIST_REQ` | 재생 가능한 센서 데이터 목록 요청 |
