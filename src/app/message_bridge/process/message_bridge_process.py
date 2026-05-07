from __future__ import annotations

from common.process.imdg_bus_process import ImdgBusProcess
from protocol.message.imdg.play import PlayReq, PlayRep
from protocol.message.imdg.playable_list import PlayableListReq, PlayableListRep
from protocol.message.message import ResponseInfo
from protocol.protocol_meta import E_PROTOCOL_ID, ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class MessageBridgeProcess(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

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
        # PLAY_REQ는 STREAMER도 broadcast로 받으므로 BRIDGE는 forward 불필요 — no-op.
        pass

    def handle_play_response(self, packet: PlayRep) -> None:
        """STREAMER → MESSAGE_BRIDGE로 들어온 PLAY_REP를 PD_PLAY_REP로 변환해 REST_SERVER로 IMDG 송신."""
        from process_category.enum_category import E_CATE
        from protocol.protocol_owner import ProtocolOwner

        response: ResponseInfo = packet.response or ResponseInfo()
        receiver = ProtocolOwner.build(E_CATE.REST_SERVER, E_CATE.E_REST_SERVER.E_COMMON.REST_SERVER)
        factory = ProtocolMeta.get_protocol_factory(E_PROTOCOL_ID.PD_PLAY_REP)
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
