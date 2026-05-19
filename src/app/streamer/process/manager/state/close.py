from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.imdg.replay.close import CloseReq

if TYPE_CHECKING:
    from app.streamer.process.manager.manager import StreamerManager


class CloseState(abState):
    owner: StreamerManager

    def on_enter(self):
        assert isinstance(self.state_param_dto, CloseReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.broadcast_message_req_inner_queue(
            E_PROTOCOL_ID.INR_CLOSE_REQ,
            self.owner.get_active_sensors(),
            rep_protocol_id=E_PROTOCOL_ID.INR_CLOSE_REP,
        )

    def on_proc_every_frame(self): pass
