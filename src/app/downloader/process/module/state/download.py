from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from python_library.state import abState

from protocol.message.process.play import InrPlayReq

from app.downloader.process.module.state.helper.download_thread import DownloadThread

if TYPE_CHECKING:
    from app.downloader.process.module.module import DownloaderModule


class DownloadState(abState):
    """InrPlayReq 수신 후 source storage → cache storage로 파일 전송.

    on_proc_once: DownloadThread 시작 (source read → cache write)
    on_proc_every_frame: thread 완료 polling → INR_PLAY_REP + WAIT 복귀
    """
    owner: DownloaderModule

    def __init__(self, state_lists, state_id) -> None:
        super().__init__(state_lists, state_id)
        self._thread: Optional[DownloadThread] = None

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrPlayReq)
        self._thread = None

    def on_leave(self):
        self._thread = None

    def on_proc_once(self):
        from sensor_category.sensor_category import SensorCategory

        assert isinstance(self.state_param_dto, InrPlayReq)
        sensor_id = self.owner.name
        category = SensorCategory.get(sensor_id)

        if category is None:
            self.__send_invalid_request(f"unknown sensor: {sensor_id}")
            self.__transition_to_wait()
            return

        source_storage = self.owner.get_storage()
        cache_storage = self.owner.get_cache_storage()
        assert source_storage is not None
        assert cache_storage is not None

        self._thread = DownloadThread(
            source_storage=source_storage,
            cache_storage=cache_storage,
            source_root=self.owner.get_storage_root(),
            source_prefix=self.owner.get_storage_prefix(),
            cache_root=self.owner.get_cache_storage_root(),
            cache_prefix=self.owner.get_cache_storage_prefix(),
            vehicle_id=self.state_param_dto.vehicle_id,
            sensor_id=sensor_id,
            category=category,
            start_time=self.state_param_dto.start_time,
            end_time=self.state_param_dto.end_time,
        )
        # CLOSE/STOP state가 진행 중 thread를 정지시킬 수 있도록 owner에 등록.
        self.owner.set_download_thread(self._thread)
        self._thread.start()

    def on_proc_every_frame(self):
        if self._thread is None:
            return
        if self._thread.is_alive():
            return

        if self._thread.get_error() is not None:
            self.__send_invalid_request(str(self._thread.get_error()))
        else:
            self.__send_ok()
        # 정상 완료 또는 에러로 thread가 끝나면 owner 등록 해제.
        self.owner.set_download_thread(None)
        self.__transition_to_wait()

    def __send_ok(self) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_PLAY_REP,
            E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
            response=make_response_info(E_CODE.OK),
        )

    def __send_invalid_request(self, reason: str) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_PLAY_REP,
            E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
            response=make_response_info(E_CODE.INVALID_REQUEST, reason=reason),
        )

    def __transition_to_wait(self) -> None:
        from app.downloader.process.module.state.state_enum import E_DOWNLOADER_MODULE_STATE

        self.owner._state_component.change_state(E_DOWNLOADER_MODULE_STATE.WAIT)
