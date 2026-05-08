from __future__ import annotations

from typing import Optional

from common.process.queue_control_process import QueueControlProcess
from protocol.message.process.pause import InrPauseReq
from protocol.message.process.play import InrPlayReq

from app.streamer.process.module.state import (
    E_STREAMER_MODULE_STATE,
    build_state_map,
)


class StreamerModule(QueueControlProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

    def on_init(self):
        super().on_init()
        self.set_state_component(
            build_state_map(),
            E_STREAMER_MODULE_STATE.WAIT,
        )

    def get_current_state_id(self) -> Optional[E_STREAMER_MODULE_STATE]:
        if self._state_component is None:
            return None
        current = self._state_component.get_state_manager().get_current_state_id()
        if current is None:
            return None
        assert isinstance(current, E_STREAMER_MODULE_STATE)
        return current

    def handle_play_request(self, packet: InrPlayReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        if self.get_current_state_id() != E_STREAMER_MODULE_STATE.WAIT:
            self.send_message_rep_inner_queue(
                E_PROTOCOL_ID.INR_PLAY_REP,
                E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if self._state_component is not None:
            self._state_component.change_state(
                E_STREAMER_MODULE_STATE.PLAY,
                state_param_dto=packet,
            )

    def handle_pause_request(self, packet: InrPauseReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        # placeholder — 실제 GStreamer pause 흐름 미이식. 어떤 state든 일단 PAUSE 진입 후 즉시 OK.
        if self._state_component is not None:
            self._state_component.change_state(
                E_STREAMER_MODULE_STATE.PAUSE,
                state_param_dto=packet,
            )
