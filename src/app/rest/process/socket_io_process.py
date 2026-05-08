from __future__ import annotations

import asyncio

from app.rest.websocket_server import SocketIOServer
from common.process.imdg_bus_process import ImdgBusProcess
from config.project_config import ProjectConfig
from protocol.message.external.ui.pause import PDPauseReq, PDPauseRep
from protocol.message.external.ui.play import PDPlayReq, PDPlayRep
from protocol.message.external.ui.playable_list import PDPlayableListReq, PDPlayableListRep
from protocol.message.message import IMessage
from protocol.protocol_meta import E_PROTOCOL_ID, ProtocolMeta
from protocol.protocol_owner import ProtocolOwner
from protocol.protocol_wrapper import ProtocolWrapper


class SocketIOProcess(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

        self.websocket_server: SocketIOServer | None = None

    def on_init(self):
        super().on_init()

        bind_ip = ProjectConfig.instance().bind_ip
        bind_port = ProjectConfig.instance().bind_port

        self.websocket_server = SocketIOServer(self, bind_ip, bind_port)
        self.websocket_server.start()

    def broadcast_to_clients(self, packet: IMessage) -> None:
        """IMDG thread에서 받은 PD response를 메인 asyncio loop로 thread-safe하게 emit."""
        if self.websocket_server is None or self.websocket_server._loop is None:
            print("[REST] websocket_server / asyncio loop 미초기화 — 응답 drop")
            return
        asyncio.run_coroutine_threadsafe(
            self.websocket_server.sio.emit("message", packet.to_json()),
            self.websocket_server._loop,
        )

    def handle_playable_list_request(self, packet: PDPlayableListReq) -> None:
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
        self.send_message_imdg(envelope)

    def handle_playable_list_response(self, packet: PDPlayableListRep) -> None:
        """PD_PLAYABLE_LIST_REP를 socket.io로 broadcast."""
        self.broadcast_to_clients(packet)

    def handle_play_request(self, packet: PDPlayReq) -> None:
        from process_category.enum_category import E_CATE

        sender = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        receiver = ProtocolOwner.build(E_CATE.STREAMER, E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER)

        message = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAY_REQ)(
            sender,
            receiver,
            packet.section_id,
            packet.vehicle_id,
            packet.sensor_id_list,
            packet.start_time,
            packet.end_time,
        )

        envelope = ProtocolWrapper.get_protocol_wrapper(message).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_play_response(self, packet: PDPlayRep) -> None:
        """PD_PLAY_REP를 socket.io로 broadcast."""
        self.broadcast_to_clients(packet)

    def handle_pause_request(self, packet: PDPauseReq) -> None:
        from process_category.enum_category import E_CATE

        sender = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        receiver = ProtocolOwner.build(E_CATE.STREAMER, E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER)

        message = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PAUSE_REQ)(
            sender,
            receiver,
        )

        envelope = ProtocolWrapper.get_protocol_wrapper(message).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_pause_response(self, packet: PDPauseRep) -> None:
        """PD_PAUSE_REP를 socket.io로 broadcast."""
        self.broadcast_to_clients(packet)
