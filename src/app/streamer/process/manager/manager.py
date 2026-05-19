from __future__ import annotations

from typing import Optional

from common.process.imdg_bus_process import ImdgBusProcess
from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.message.imdg.replay.close import CloseReq
from protocol.message.imdg.replay.pause import PauseReq
from protocol.message.imdg.replay.play import PlayReq
from protocol.message.imdg.replay.seek import SeekReq
from protocol.message.imdg.replay.stop import StopReq
from protocol.message.message import IMessage

from app.streamer.process.manager.state import (
    E_STREAMER_MANAGER_STATE,
    build_state_map,
)


class StreamerManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self.enable_inr_matcher()
        # PLAY 시점에 저장 — PAUSE/SEEK/CLOSE/STOP broadcast 시 동일 sensor 집합 사용.
        self._active_sensors: list[str] = []

    def set_active_sensors(self, sensors: list[str]) -> None:
        self._active_sensors = sensors

    def get_active_sensors(self) -> list[str]:
        return self._active_sensors

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

        # BRIDGE-orchestrated 흐름만 처리. REST 직접 broadcast나 타 receiver 무시.
        if not ProtocolOwner.is_owner(packet.sender, E_CATE.MESSAGE_BRIDGE):
            return
        if not ProtocolOwner.is_owner(packet.receiver, E_CATE.STREAMER):
            return

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

    def handle_pause_request(self, packet: PauseReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        if self.get_current_state_id() != E_STREAMER_MANAGER_STATE.PLAY:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.PAUSE_REP,
                ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.PAUSE, state_param_dto=packet)

    def handle_pause_response(self, packet) -> None:
        # 매처 경로(handle_pause_group_response)가 후처리 — 개별 handler는 no-op.
        pass

    def handle_pause_group_response(self, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        bridge = ProtocolOwner.build(
            E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE
        )

        if pair_state == E_PROTOCOL_PAIR_STATE.ERROR:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.PAUSE_REP, bridge,
                response=make_response_info(E_CODE.INVALID_REQUEST, "module error"),
            )
        else:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.PAUSE_REP, bridge,
                response=make_response_info(E_CODE.OK),
            )

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.WAIT)

    def handle_seek_request(self, packet: SeekReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        # Seek은 PLAY 또는 PAUSE 중에 의미 있음 — WAIT일 때는 INVALID_REQUEST.
        current = self.get_current_state_id()
        if current not in (E_STREAMER_MANAGER_STATE.PLAY, E_STREAMER_MANAGER_STATE.PAUSE):
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.SEEK_REP,
                ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.SEEK, state_param_dto=packet)

    def handle_seek_response(self, packet) -> None:
        # 매처 경로(handle_seek_group_response)가 후처리 — 개별 handler는 no-op.
        pass

    def handle_seek_group_response(self, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        bridge = ProtocolOwner.build(
            E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE
        )

        if pair_state == E_PROTOCOL_PAIR_STATE.ERROR:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.SEEK_REP, bridge,
                response=make_response_info(E_CODE.INVALID_REQUEST, "module error"),
            )
        else:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.SEEK_REP, bridge,
                response=make_response_info(E_CODE.OK),
            )

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.WAIT)

    def handle_close_request(self, packet: CloseReq) -> None:
        # Close는 어떤 state에서든 의미 있음(현재 활성 흐름 종료) — state 체크 생략하고 일단 CLOSE 진입.
        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.CLOSE, state_param_dto=packet)

    def handle_close_response(self, packet) -> None:
        # 매처 경로(handle_close_group_response)가 후처리 — 개별 handler는 no-op.
        pass

    def handle_close_group_response(self, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        bridge = ProtocolOwner.build(
            E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE
        )

        if pair_state == E_PROTOCOL_PAIR_STATE.ERROR:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.CLOSE_REP, bridge,
                response=make_response_info(E_CODE.INVALID_REQUEST, "module error"),
            )
        else:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.CLOSE_REP, bridge,
                response=make_response_info(E_CODE.OK),
            )

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.WAIT)

    def handle_stop_request(self, packet: StopReq) -> None:
        # Stop은 어떤 state에서든 의미 있음(현재 활성 흐름 종료) — state 체크 생략하고 일단 STOP 진입.
        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.STOP, state_param_dto=packet)

    def handle_stop_response(self, packet) -> None:
        # 매처 경로(handle_stop_group_response)가 후처리 — 개별 handler는 no-op.
        pass

    def handle_stop_group_response(self, pair_state: E_PROTOCOL_PAIR_STATE, packets: list[IMessage]) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        bridge = ProtocolOwner.build(
            E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE
        )

        if pair_state == E_PROTOCOL_PAIR_STATE.ERROR:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.STOP_REP, bridge,
                response=make_response_info(E_CODE.INVALID_REQUEST, "module error"),
            )
        else:
            self.send_message_rep_imdg(
                E_PROTOCOL_ID.STOP_REP, bridge,
                response=make_response_info(E_CODE.OK),
            )

        if self._state_component is not None:
            self._state_component.change_state(E_STREAMER_MANAGER_STATE.WAIT)
