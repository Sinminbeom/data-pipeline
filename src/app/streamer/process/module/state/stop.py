from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.process.replay.stop import InrStopReq

if TYPE_CHECKING:
    from app.streamer.process.module.module import StreamerModule


class StopState(abState):
    """player 종료 + None reset. Close와 동일 동작."""
    owner: StreamerModule

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrStopReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        player = self.owner.get_player()
        if player is not None:
            try:
                player.stop()
            except Exception:
                pass
            self.owner.set_player(None)

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_STOP_REP,
            E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
            response=make_response_info(E_CODE.OK),
        )

        from app.streamer.process.module.state.state_enum import E_STREAMER_MODULE_STATE
        self.owner._state_component.change_state(E_STREAMER_MODULE_STATE.WAIT)

    def on_proc_every_frame(self): pass
