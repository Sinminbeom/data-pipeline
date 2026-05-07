from __future__ import annotations

from typing import Optional

from common.process.imdg_bus_process import ImdgBusProcess
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper
from protocol.section_element import SectionElement, SectionElementContainer

from app.downloader.process.manager.state import (
    E_DOWNLOADER_MANAGER_STATE,
    build_state_map,
)


class DownloaderManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        # broadcast scatter-gather 응답 누적 매처 활성화
        # 매처가 발화한 group handler에서 후처리 일괄 수행 — PlayableState는 broadcast만.
        self.enable_inr_matcher()

    def on_init(self):
        super().on_init()
        self.set_state_component(
            build_state_map(),
            E_DOWNLOADER_MANAGER_STATE.WAIT,
        )

    def get_current_state_id(self) -> Optional[E_DOWNLOADER_MANAGER_STATE]:
        if self._state_component is None:
            return None
        current = self._state_component.get_state_manager().get_current_state_id()
        if current is None:
            return None
        assert isinstance(current, E_DOWNLOADER_MANAGER_STATE)
        return current

    @staticmethod
    def playable_list_request(process: DownloaderManager, wrapper: ProtocolWrapper, packet: IMessage):
        from process_category.enum_category import E_CATE
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner
        from protocol.protocol_code import E_CODE, make_response_info

        if process.get_current_state_id() != E_DOWNLOADER_MANAGER_STATE.WAIT:
            process.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAYABLE_LIST_REP,
                ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
                None,
                None,
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if process._state_component is not None:
            process._state_component.change_state(E_DOWNLOADER_MANAGER_STATE.PLAYABLE, state_param_dto=packet)

    @staticmethod
    def playable_list_response(process: DownloaderManager, wrapper: ProtocolWrapper, packet: IMessage):
        # 매처 경로(playable_list_group_response)가 모든 후처리를 담당하므로 개별 핸들러는 no-op.
        # listener가 receive_handlers를 항상 dispatch하므로 빈 stub은 유지 (KeyError 방지).
        pass

    @staticmethod
    def playable_list_group_response(process, pair_state, packets):
        """모든 모듈의 INR_PLAYABLE_LIST_REP 도착 시 매처 인프라가 발화.

        교집합 계산 + PLAYABLE_LIST_REP 송신 + DOWNLOAD_READY 전이를 한 곳에서 수행.
        InnerQueueListener thread에서 실행되지만:
          - send_message_rep_imdg → redis-py thread-safe
          - change_state → 다음 메인 loop frame에 적용되는 reservation
        """
        from process_category.enum_category import E_CATE
        from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
        from protocol.message.process.playable_list import InrPlayableListRep
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        bridge = ProtocolOwner.build(
            E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE
        )

        # 1) ERROR — INVALID_REQUEST 응답 후 WAIT 복귀
        if pair_state == E_PROTOCOL_PAIR_STATE.ERROR:
            process.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAYABLE_LIST_REP, bridge, None, None,
                response=make_response_info(E_CODE.INVALID_REQUEST, "module error"),
            )
            if process._state_component is not None:
                process._state_component.change_state(E_DOWNLOADER_MANAGER_STATE.WAIT)
            return

        # 2) COMPLEATE — packets에서 sensor별 sections 복원 + 1초 grid 펼치기 + N-way 교집합
        one_dim_lists: list[list[str]] = []
        sensor_ids: list[str] = []
        for packet in packets:
            assert isinstance(packet, InrPlayableListRep)
            sensor_ids.append(packet.sensor_id)

            elements: list[SectionElement] = []
            for raw in packet.section_list:
                if isinstance(raw, SectionElement):
                    elements.append(raw)
                elif isinstance(raw, dict):
                    elements.append(SectionElement(**raw))
            one_dim_lists.append(
                SectionElementContainer(elements).convert_one_dimensional_list()
            )

        playable_list = SectionElementContainer.calculate_intersection(*one_dim_lists)

        # 3) PLAYABLE_LIST_REP 송신
        process.send_message_rep_imdg(
            E_PROTOCOL_ID.PLAYABLE_LIST_REP,
            bridge,
            sensor_ids,
            playable_list,
            response=make_response_info(E_CODE.OK),
        )

        # 4) DOWNLOAD_READY 전이 (reservation — 다음 메인 frame에 적용됨)
        if process._state_component is not None:
            process._state_component.change_state(E_DOWNLOADER_MANAGER_STATE.DOWNLOAD_READY)
