import asyncio
import json
from abc import ABC, abstractmethod

import socketio
from fastapi import FastAPI
import uvicorn

from common.process.queue_control_process import QueueControlProcess
from protocol.protocol_meta import ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class abWebSocketServer(ABC):
    """
    FastAPI + python-socketio(ASGI)

    - FastAPI app: self.fastapi_app
    - Socket.IO server: self.sio (AsyncServer)
    - ASGI app (FastAPI + SocketIO 결합): self.app (ASGIApp)
    """

    def __init__(self, _parents_process: QueueControlProcess, _bind_ip: str = "0.0.0.0", _port: int = 9999):
        self.parents_process: QueueControlProcess = _parents_process

        self.bindIP = _bind_ip
        self.port = _port

        self.fastapi_app = FastAPI()

        # Socket.IO (ASGI)
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",     # 필요 시 제한 권장
            allow_upgrades=False,         # 기존 코드와 동일 옵션
            logger=False,
            engineio_logger=False,
        )

        # FastAPI + Socket.IO 결합 ASGI 앱
        # socketio_path는 클라이언트의 연결 경로와 맞춰야 합니다(기본: /socket.io).
        self.app = socketio.ASGIApp(self.sio, other_asgi_app=self.fastapi_app)

        # IMDG listener thread에서 sio.emit (coroutine)을 스케줄하기 위해
        # uvicorn 기동 시점의 asyncio loop을 캐싱한다.
        self._loop: asyncio.AbstractEventLoop | None = None

        self.init()

    def init(self) -> None:
        self.on_init()

    def start(self) -> None:
        uvicorn.run(self.app, host=self.bindIP, port=self.port, log_level="info")

    @abstractmethod
    def on_init(self) -> None:
        pass

    def get_parent_process(self) -> QueueControlProcess:
        return self.parents_process


class SocketIOServer(abWebSocketServer):
    """순수 ASGI server — 외부 socket.io 클라이언트의 진입점.

    receive handler는 SocketIOProcess에 위치한다 (다른 카테고리와 일관).
    """

    def __init__(self, _parents_process: QueueControlProcess, _bind_ip: str = "0.0.0.0", _bind_port: int = 9999):
        super().__init__(_parents_process, _bind_ip, _bind_port)

    def on_init(self) -> None:
        @self.fastapi_app.on_event("startup")
        async def _capture_event_loop():
            # uvicorn이 띄운 asyncio loop을 캡처해두면 IMDG thread에서 emit 가능.
            self._loop = asyncio.get_running_loop()

        # Socket.IO event — 외부 클라이언트 → REST_SERVER 진입점
        @self.sio.on("message")
        async def request(sid: str, message: str):
            parsed_dict = json.loads(message)

            protocol_id = parsed_dict["protocol_id"]
            receiver_name = parsed_dict["receiver"]

            if receiver_name != self.get_parent_process().get_app_name():
                print("Rest Server Recv Packet MissMatch!!")
                return

            packet = ProtocolMeta.get_json_decoder(protocol_id)(message)
            wrapper = ProtocolWrapper.get_protocol_wrapper(packet)

            recv_handler = ProtocolMeta.get_receive_handler(protocol_id, receiver_name)
            recv_handler(self.get_parent_process(), wrapper, packet)
