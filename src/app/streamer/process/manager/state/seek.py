from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.imdg.seek import SeekReq

if TYPE_CHECKING:
    from app.streamer.process.manager.manager import StreamerManager


class SeekState(abState):
    owner: StreamerManager

    def on_enter(self):
        assert isinstance(self.state_param_dto, SeekReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from protocol.protocol_meta import E_PROTOCOL_ID

        assert isinstance(self.state_param_dto, SeekReq)

        # 활성 sensor module list 추적은 후속 작업 — placeholder는 빈 리스트.
        receivers: list[str] = []

        self.owner.broadcast_message_req_inner_queue(
            E_PROTOCOL_ID.INR_SEEK_REQ,
            receivers,
            self.state_param_dto.start_time,
            rep_protocol_id=E_PROTOCOL_ID.INR_SEEK_REP,
        )

    def on_proc_every_frame(self): pass
