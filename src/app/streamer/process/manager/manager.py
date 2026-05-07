from __future__ import annotations

from typing import Optional

from common.process.imdg_bus_process import ImdgBusProcess
from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.message.imdg.play import PlayReq
from protocol.message.message import IMessage

from app.streamer.process.manager.state import (
    E_STREAMER_MANAGER_STATE,
    build_state_map,
)


class StreamerManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self.enable_inr_matcher()

    def on_init(self):
        super().on_init()
        self.set_state_component(
            build_state_map(),
            E_STREAMER_MANAGER_STATE.WAIT,
        )

    def get_current_state_id(self) -> Optional[E_STREAMER_MANAGER_STATE]:
        if self._state_component is None:
            return None
        current = self._state_component.get_state_manager().get_current_state_id()
        if current is None:
            return None
        assert isinstance(current, E_STREAMER_MANAGER_STATE)
        return current

    def handle_play_request(self, packet: PlayReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        if self.get_current_state_id() != E_STREAMER_MANAGER_STATE.WAIT:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAY_REP,
                ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.PLAY, state_param_dto=packet)

    def handle_play_response(self, packet) -> None:
        # 매처 경로(handle_play_group_response)가 후처리 — 개별 handler는 no-op.
        pass

    def handle_play_group_response(self, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        bridge = ProtocolOwner.build(
            E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE
        )

        if pair_state == E_PROTOCOL_PAIR_STATE.ERROR:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAY_REP, bridge,
                response=make_response_info(E_CODE.INVALID_REQUEST, "module error"),
            )
        else:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAY_REP, bridge,
                response=make_response_info(E_CODE.OK),
            )

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.WAIT)
