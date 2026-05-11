from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.process.play import InrPlayReq

if TYPE_CHECKING:
    from app.downloader.process.module.module import DownloaderModule


class DownloadState(abState):
    """InrPlayReq 수신 후 다운로드 본체를 수행할 상태.

    Phase 1: 진입만 수행 — 실제 파일 read/write는 후속 phase.
    """
    owner: DownloaderModule

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrPlayReq)

    def on_leave(self): pass
    def on_proc_once(self): pass
    def on_proc_every_frame(self): pass
