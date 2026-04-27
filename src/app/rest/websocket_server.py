import json
from abc import ABC, abstractmethod

import socketio
from fastapi import FastAPI
import uvicorn

from common.process.imdg_bus_process import IImdgBusProcess
from common.process.queue_control_process import QueueControlProcess
from protocol.message.external.ui.playable_list import PDPlayableListReq
from protocol.protocol_meta import ProtocolMeta, E_PROTOCOL_ID
from protocol.protocol_owner import ProtocolOwner
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
    def __init__(self, _parents_process: QueueControlProcess, _bind_ip: str = "0.0.0.0", _bind_port: int = 9999):
        super().__init__(_parents_process, _bind_ip, _bind_port)

    @staticmethod
    def playable_list_request(
        process: IImdgBusProcess,
        wrapper: ProtocolWrapper,
        packet: PDPlayableListReq,
    ):
        from process_category.enum_category import E_CATE


        sender = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        receiver = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)

        message = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAYABLE_LIST_REQ)(
            sender,
            receiver,
            packet.vehicle_id,
            packet.sensor_id_list,
            packet.start_time,
            packet.end_time,
        )

        envelope = ProtocolWrapper.get_protocol_wrapper(message).get_protocol_packet_message()
        process.send_message_imdg(envelope)

    def on_init(self) -> None:
        self.get_parent_process().on_register_handler(ProtocolMeta.get_receive_handler_container())


        # Socket.IO event
        @self.sio.on("message")
        async def request(sid: str, message: str):
            print("message : " + message)

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
