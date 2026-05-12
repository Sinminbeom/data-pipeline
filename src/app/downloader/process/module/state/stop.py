from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.process.stop import InrStopReq

if TYPE_CHECKING:
    from app.downloader.process.module.module import DownloaderModule


class StopState(abState):
    """진행 중 DownloadThread 정지 + None reset. Close와 동일 동작 (replayer 미러)."""
    owner: DownloaderModule

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrStopReq)

    def on_leave(self): pass

    def on_proc_once(self):
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        thread = self.owner.get_download_thread()
        if thread is not None:
            try:
                thread.stop()
                thread.join()
            except Exception:
                pass
            self.owner.set_download_thread(None)

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_STOP_REP,
            E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
            response=make_response_info(E_CODE.OK),
        )

        from app.downloader.process.module.state.state_enum import E_DOWNLOADER_MODULE_STATE
        self.owner._state_component.change_state(E_DOWNLOADER_MODULE_STATE.WAIT)

    def on_proc_every_frame(self): pass
