from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.imdg.pause import PauseReq

if TYPE_CHECKING:
    from app.streamer.process.manager.manager import StreamerManager


class PauseState(abState):
    owner: StreamerManager

    def on_enter(self):
        assert isinstance(self.state_param_dto, PauseReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from protocol.protocol_meta import E_PROTOCOL_ID

        # 모든 sensor module에 INR_PAUSE_REQ broadcast.
        # receiver_process_names는 Streamer Manager가 보유한 module list — 현 placeholder는 빈 리스트.
        # 실제 sensor list 추적은 PLAY state 진입 시 owner에 저장 필요 (후속 작업).
        receivers: list[str] = []

        self.owner.broadcast_message_req_inner_queue(
            E_PROTOCOL_ID.INR_PAUSE_REQ,
            receivers,
            rep_protocol_id=E_PROTOCOL_ID.INR_PAUSE_REP,
        )

    def on_proc_every_frame(self): pass
