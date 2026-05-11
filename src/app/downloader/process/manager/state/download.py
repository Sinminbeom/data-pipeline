from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.imdg.play import PlayReq

if TYPE_CHECKING:
    from app.downloader.process.manager.manager import DownloaderManager


class DownloadState(abState):
    """PlayReq 수신 후 모듈에 INR_PLAY_REQ를 broadcast하는 상태.

    Phase 1: 진입 시 broadcast만 수행. 모듈 응답 후처리(group response)는 후속 phase.
    """
    owner: DownloaderManager

    def on_enter(self):
        assert isinstance(self.state_param_dto, PlayReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from protocol.protocol_meta import E_PROTOCOL_ID

        assert isinstance(self.state_param_dto, PlayReq)

        self.owner.broadcast_message_req_inner_queue(
            E_PROTOCOL_ID.INR_PLAY_REQ,
            self.state_param_dto.sensor_id_list,
            self.state_param_dto.section_id,
            self.state_param_dto.vehicle_id,
            self.state_param_dto.start_time,
            self.state_param_dto.end_time,
            rep_protocol_id=E_PROTOCOL_ID.INR_PLAY_REP,
        )

    def on_proc_every_frame(self): pass
