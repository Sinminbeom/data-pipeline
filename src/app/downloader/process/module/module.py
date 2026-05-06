from __future__ import annotations

from typing import Optional

from python_library.storage.local.local_storage_factory import LocalStorageFactory
from python_library.storage.local.local_storage_info_factory import LocalStorageInfoFactory
from python_library.storage.storage import IStorage

from common.process.queue_control_process import QueueControlProcess
from config.project_config import ProjectConfig
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper

from app.downloader.process.module.state import (
    E_DOWNLOADER_MODULE_STATE,
    build_state_map,
)


class DownloaderModule(QueueControlProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._storage: Optional[IStorage] = None
        self._storage_root: str = ""
        self._storage_prefix: str = ""

    def on_init(self):
        super().on_init()
        config = ProjectConfig.instance()
        self._storage_root = (config.storage_root or "").rstrip("/")
        self._storage_prefix = (config.storage_prefix or "").strip("/")
        self._storage = LocalStorageFactory(LocalStorageInfoFactory()).create_storage()
        self._storage.connect()

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

    @staticmethod
    def playable_list_request(process: DownloaderModule, wrapper: ProtocolWrapper, packet: IMessage):
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        if process.get_current_state_id() != E_DOWNLOADER_MODULE_STATE.WAIT:
            process.send_message_rep_inner_queue(
                E_PROTOCOL_ID.INR_PLAYABLE_LIST_REP,
                E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
                process.name,
                [],
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if process._state_component is not None:
            process._state_component.change_state(
                E_DOWNLOADER_MODULE_STATE.PLAYABLE,
                state_param_dto=packet,
            )
