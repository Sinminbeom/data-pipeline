from __future__ import annotations

from typing import Optional

from common.process.imdg_bus_process import ImdgBusProcess
from protocol.message.imdg.close import CloseReq, CloseRep
from protocol.message.imdg.pause import PauseReq, PauseRep
from protocol.message.imdg.play import PlayReq, PlayRep
from protocol.message.imdg.seek import SeekReq, SeekRep
from protocol.message.imdg.stop import StopReq, StopRep
from protocol.message.imdg.playable_list import PlayableListReq, PlayableListRep
from protocol.message.message import ResponseInfo
from protocol.protocol_meta import E_PROTOCOL_ID, ProtocolMeta
from protocol.protocol_owner import ProtocolOwner
from protocol.protocol_wrapper import ProtocolWrapper


class MessageBridgeProcess(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        # PLAY_REQ 직렬화 상태 — REST→DOWNLOADER→STREAMER 흐름 사이에 보관.
        # single-flight 가정 (동시에 하나의 PLAY_REQ만 진행).
        self._pending_play_req: Optional[PlayReq] = None

    def handle_playable_list_request(self, packet: PlayableListReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner

        sender = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)
        receiver = ProtocolOwner.build(E_CATE.DOWNLOADER, E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAYABLE_LIST_REQ)
        fwd_packet = factory(
            sender,
            receiver,
            packet.vehicle_id,
            packet.sensor_id_list,
            packet.start_time,
            packet.end_time,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_playable_list_response(self, packet: PlayableListRep) -> None:
        """DOWNLOADER에서 받은 PLAYABLE_LIST_REP를 PD_PLAYABLE_LIST_REP로 변환해 REST_SERVER로 IMDG 송신."""
        from process_category.enum_category import E_CATE
        from protocol.message.external.ui.section_element import PDSectionElement
        from protocol.protocol_owner import ProtocolOwner

        # IMDG section_list는 list[dict] (jsonpickle 미사용 + asdict 직렬화) 또는 list[SectionElement]
        pd_sections: list[PDSectionElement] = []
        for raw in packet.section_list:
            if isinstance(raw, dict):
                pd_sections.append(PDSectionElement(
                    sectionId=raw["section_id"],
                    startTime=raw["start_time"],
                    endTime=raw["end_time"],
                ))
            else:
                pd_sections.append(PDSectionElement(
                    sectionId=raw.section_id,
                    startTime=raw.start_time,
                    endTime=raw.end_time,
                ))

        response: ResponseInfo = packet.response or ResponseInfo()
        receiver = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PD_PLAYABLE_LIST_REP)
        sender = ProtocolOwner.build(self.get_app_name(), self.name)

        fwd_packet = factory(
            sender,
            receiver,
            packet.sensor_id_list,
            pd_sections,
            response.code,
            response.code_nm,
            response.reason,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_play_request(self, packet: PlayReq) -> None:
        """REST에서 받은 PLAY_REQ를 DOWNLOADER에 forward (직렬화 시작).

        STREAMER에는 DOWNLOADER 완료(handle_play_response) 후 forward.
        BRIDGE 자신이 send한 PLAY_REQ도 receive_handlers로 dispatch되므로 sender로 필터.
        """
        from process_category.enum_category import E_CATE

        if not ProtocolOwner.is_owner(packet.sender, E_CATE.REST_SERVER):
            # REST 외 sender(BRIDGE 자신의 forward 등)는 무시.
            return

        self._pending_play_req = packet
        self.__forward_play_req(packet, target_app=E_CATE.DOWNLOADER,
                                target_proc=E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER)

    def handle_play_response(self, packet: PlayRep) -> None:
        """PLAY_REP 분기:
        - DOWNLOADER 발신 + OK → STREAMER에 PLAY_REQ forward
        - DOWNLOADER 발신 + ERROR → REST에 PD_PLAY_REP error forward (STREAMER skip)
        - STREAMER 발신 → REST에 PD_PLAY_REP forward (최종 응답)
        """
        from process_category.enum_category import E_CATE

        response: ResponseInfo = packet.response or ResponseInfo()

        if ProtocolOwner.is_owner(packet.sender, E_CATE.DOWNLOADER):
            # 에러면 STREAMER 트리거 안 하고 즉시 REST로 응답.
            if response.code != "OK":
                self._pending_play_req = None
                self.__forward_pd_play_rep(response)
                return

            pending = self._pending_play_req
            if pending is None:
                # 방어적: state 유실 — 그래도 STREAMER에 보낼 정보가 없으므로 error 응답.
                self.__forward_pd_play_rep(ResponseInfo(code="ERROR", code_nm="ERROR",
                                                       reason="pending play_req lost"))
                return

            self.__forward_play_req(pending, target_app=E_CATE.STREAMER,
                                    target_proc=E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER)
            return

        # STREAMER → REST 최종 forward.
        self._pending_play_req = None
        self.__forward_pd_play_rep(response)

    def __forward_play_req(self, source: PlayReq, target_app: str, target_proc: str) -> None:
        sender = ProtocolOwner.build(self.get_app_name(), self.name)
        receiver = ProtocolOwner.build(target_app, target_proc)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PLAY_REQ)
        fwd_packet = factory(
            sender, receiver,
            source.section_id, source.vehicle_id, source.sensor_id_list,
            source.start_time, source.end_time,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def __forward_pd_play_rep(self, response: ResponseInfo) -> None:
        from process_category.enum_category import E_CATE

        receiver = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PD_PLAY_REP)
        sender = ProtocolOwner.build(self.get_app_name(), self.name)

        fwd_packet = factory(
            sender, receiver,
            response.code, response.code_nm, response.reason,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_pause_request(self, packet: PauseReq) -> None:
        """REST에서 받은 PAUSE_REQ를 STREAMER에 forward.

        BRIDGE 자신이 send한 PAUSE_REQ도 receive_handlers로 dispatch되므로 sender로 필터.
        """
        from process_category.enum_category import E_CATE

        if not ProtocolOwner.is_owner(packet.sender, E_CATE.REST_SERVER):
            return

        sender = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)
        receiver = ProtocolOwner.build(E_CATE.STREAMER, E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PAUSE_REQ)
        fwd_packet = factory(sender, receiver)
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_pause_response(self, packet: PauseRep) -> None:
        """STREAMER → MESSAGE_BRIDGE로 들어온 PAUSE_REP를 PD_PAUSE_REP로 변환해 REST_SERVER로 IMDG 송신."""
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner

        response: ResponseInfo = packet.response or ResponseInfo()
        receiver = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PD_PAUSE_REP)
        sender = ProtocolOwner.build(self.get_app_name(), self.name)

        fwd_packet = factory(
            sender,
            receiver,
            response.code,
            response.code_nm,
            response.reason,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_seek_request(self, packet: SeekReq) -> None:
        """REST에서 받은 SEEK_REQ를 STREAMER에 forward.

        BRIDGE 자신이 send한 SEEK_REQ도 receive_handlers로 dispatch되므로 sender로 필터.
        """
        from process_category.enum_category import E_CATE

        if not ProtocolOwner.is_owner(packet.sender, E_CATE.REST_SERVER):
            return

        sender = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)
        receiver = ProtocolOwner.build(E_CATE.STREAMER, E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.SEEK_REQ)
        fwd_packet = factory(sender, receiver, packet.start_time)
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_seek_response(self, packet: SeekRep) -> None:
        """STREAMER → MESSAGE_BRIDGE로 들어온 SEEK_REP를 PD_SEEK_REP로 변환해 REST_SERVER로 IMDG 송신."""
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner

        response: ResponseInfo = packet.response or ResponseInfo()
        receiver = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PD_SEEK_REP)
        sender = ProtocolOwner.build(self.get_app_name(), self.name)

        fwd_packet = factory(
            sender,
            receiver,
            response.code,
            response.code_nm,
            response.reason,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_close_request(self, packet: CloseReq) -> None:
        """REST에서 받은 CLOSE_REQ를 STREAMER에 forward.

        BRIDGE 자신이 send한 CLOSE_REQ도 receive_handlers로 dispatch되므로 sender로 필터.
        """
        from process_category.enum_category import E_CATE

        if not ProtocolOwner.is_owner(packet.sender, E_CATE.REST_SERVER):
            return

        sender = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)
        receiver = ProtocolOwner.build(E_CATE.STREAMER, E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.CLOSE_REQ)
        fwd_packet = factory(sender, receiver)
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_close_response(self, packet: CloseRep) -> None:
        """STREAMER → MESSAGE_BRIDGE로 들어온 CLOSE_REP를 PD_CLOSE_REP로 변환해 REST_SERVER로 IMDG 송신."""
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner

        response: ResponseInfo = packet.response or ResponseInfo()
        receiver = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PD_CLOSE_REP)
        sender = ProtocolOwner.build(self.get_app_name(), self.name)

        fwd_packet = factory(
            sender,
            receiver,
            response.code,
            response.code_nm,
            response.reason,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_stop_request(self, packet: StopReq) -> None:
        """REST에서 받은 STOP_REQ를 STREAMER에 forward.

        BRIDGE 자신이 send한 STOP_REQ도 receive_handlers로 dispatch되므로 sender로 필터.
        """
        from process_category.enum_category import E_CATE

        if not ProtocolOwner.is_owner(packet.sender, E_CATE.REST_SERVER):
            return

        sender = ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE)
        receiver = ProtocolOwner.build(E_CATE.STREAMER, E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.STOP_REQ)
        fwd_packet = factory(sender, receiver)
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)

    def handle_stop_response(self, packet: StopRep) -> None:
        """STREAMER → MESSAGE_BRIDGE로 들어온 STOP_REP를 PD_STOP_REP로 변환해 REST_SERVER로 IMDG 송신."""
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner

        response: ResponseInfo = packet.response or ResponseInfo()
        receiver = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PD_STOP_REP)
        sender = ProtocolOwner.build(self.get_app_name(), self.name)

        fwd_packet = factory(
            sender,
            receiver,
            response.code,
            response.code_nm,
            response.reason,
        )
        envelope = ProtocolWrapper.get_protocol_wrapper(fwd_packet).get_protocol_packet_message()
        self.send_message_imdg(envelope)
