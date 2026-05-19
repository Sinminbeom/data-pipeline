from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.process.replay.seek import InrSeekReq

if TYPE_CHECKING:
    from app.streamer.process.module.module import StreamerModule


class SeekState(abState):
    """reader cursor 재설정 — pool clear + 새 reader 시작. player 유지."""
    owner: StreamerModule

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrSeekReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        assert isinstance(self.state_param_dto, InrSeekReq)

        player = self.owner.get_player()
        if player is None:
            self.__send_invalid_request("player not active")
            self.__transition_to_wait()
            return

        try:
            player.seek(self.state_param_dto.start_time)
        except Exception as exc:
            self.__send_invalid_request(str(exc))
            self.__transition_to_wait()
            return

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_SEEK_REP,
            E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
            response=make_response_info(E_CODE.OK),
        )
        self.__transition_to_wait()

    def on_proc_every_frame(self): pass

    def __send_invalid_request(self, reason: str) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_SEEK_REP,
            E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
            response=make_response_info(E_CODE.INVALID_REQUEST, reason=reason),
        )

    def __transition_to_wait(self) -> None:
        from app.streamer.process.module.state.state_enum import E_STREAMER_MODULE_STATE
        self.owner._state_component.change_state(E_STREAMER_MODULE_STATE.WAIT)
