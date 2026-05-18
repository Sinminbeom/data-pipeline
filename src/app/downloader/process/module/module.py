from __future__ import annotations

from typing import Optional

from python_library.storage.local.local_storage_factory import LocalStorageFactory
from python_library.storage.local.local_storage_info_factory import LocalStorageInfoFactory
from python_library.storage.s3.s3_storage_factory import S3StorageFactory
from python_library.storage.s3.s3_storage_info_factory import S3StorageInfoFactory
from python_library.storage.storage import IStorage

from common.process.queue_control_process import QueueControlProcess
from config.project_config import ProjectConfig
from protocol.message.process.close import InrCloseReq
from protocol.message.process.play import InrPlayReq
from protocol.message.process.playable_list import InrPlayableListReq
from protocol.message.process.stop import InrStopReq

from app.downloader.process.module.state import (
    E_DOWNLOADER_MODULE_STATE,
    build_state_map,
)
from app.downloader.process.module.state.helper.download_thread import DownloadThread


class DownloaderModule(QueueControlProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._storage: Optional[IStorage] = None
        self._storage_root: str = ""
        self._storage_prefix: str = ""
        self._cache_storage: Optional[IStorage] = None
        self._cache_storage_root: str = ""
        self._cache_storage_prefix: str = ""
        # 진행 중 DownloadThread 참조. CLOSE/STOP state에서 정지 신호 발신용.
        self._download_thread: Optional[DownloadThread] = None

    def on_init(self):
        super().on_init()
        config = ProjectConfig.instance()
        self._storage_root = (config.storage_root or "").rstrip("/")
        self._storage_prefix = (config.storage_prefix or "").strip("/")
        self._storage = S3StorageFactory(S3StorageInfoFactory()).create_storage()
        self._storage.connect()

        self._cache_storage_root = (config.cache_storage_root or "").rstrip("/")
        self._cache_storage_prefix = (config.cache_storage_prefix or "").strip("/")
        self._cache_storage = LocalStorageFactory(LocalStorageInfoFactory()).create_storage()
        self._cache_storage.connect()

        self.set_state_component(
            build_state_map(),
            E_DOWNLOADER_MODULE_STATE.WAIT,
        )

    def get_current_state_id(self) -> Optional[E_DOWNLOADER_MODULE_STATE]:
        if self._state_component is None:
            return None
        current = self._state_component.get_state_manager().get_current_state_id()
        if current is None:
            return None
        assert isinstance(current, E_DOWNLOADER_MODULE_STATE)
        return current

    def get_storage(self) -> Optional[IStorage]:
        return self._storage

    def get_storage_root(self) -> str:
        return self._storage_root

    def get_storage_prefix(self) -> str:
        return self._storage_prefix

    def get_cache_storage(self) -> Optional[IStorage]:
        return self._cache_storage

    def get_cache_storage_root(self) -> str:
        return self._cache_storage_root

    def get_cache_storage_prefix(self) -> str:
        return self._cache_storage_prefix

    def get_download_thread(self) -> Optional[DownloadThread]:
        return self._download_thread

    def set_download_thread(self, thread: Optional[DownloadThread]) -> None:
        self._download_thread = thread

    def handle_playable_list_request(self, packet: InrPlayableListReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        if self.get_current_state_id() != E_DOWNLOADER_MODULE_STATE.WAIT:
            self.send_message_rep_inner_queue(
                E_PROTOCOL_ID.INR_PLAYABLE_LIST_REP,
                E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
                self.name,
                [],
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if self._state_component is not None:
            self._state_component.change_state(
                E_DOWNLOADER_MODULE_STATE.PLAYABLE,
                state_param_dto=packet,
            )

    def handle_play_request(self, packet: InrPlayReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        if self.get_current_state_id() != E_DOWNLOADER_MODULE_STATE.DOWNLOAD_READY:
            self.send_message_rep_inner_queue(
                E_PROTOCOL_ID.INR_PLAY_REP,
                E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if self._state_component is not None:
            self._state_component.change_state(
                E_DOWNLOADER_MODULE_STATE.DOWNLOAD,
                state_param_dto=packet,
            )

    def handle_close_request(self, packet: InrCloseReq) -> None:
        # 어느 state에서든 진입 허용 (streamer pattern 동일).
        if self._state_component is not None:
            self._state_component.change_state(
                E_DOWNLOADER_MODULE_STATE.CLOSE,
                state_param_dto=packet,
            )

    def handle_stop_request(self, packet: InrStopReq) -> None:
        # 어느 state에서든 진입 허용 (streamer pattern 동일).
        if self._state_component is not None:
            self._state_component.change_state(
                E_DOWNLOADER_MODULE_STATE.STOP,
                state_param_dto=packet,
            )
