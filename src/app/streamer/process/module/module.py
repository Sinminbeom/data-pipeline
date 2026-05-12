from __future__ import annotations

from typing import Optional

from python_library.storage.local.local_storage_factory import LocalStorageFactory
from python_library.storage.local.local_storage_info_factory import LocalStorageInfoFactory
from python_library.storage.storage import IStorage

from common.process.queue_control_process import QueueControlProcess
from config.project_config import ProjectConfig
from protocol.message.process.close import InrCloseReq
from protocol.message.process.pause import InrPauseReq
from protocol.message.process.play import InrPlayReq
from protocol.message.process.seek import InrSeekReq
from protocol.message.process.stop import InrStopReq

from app.streamer.process.module.state import (
    E_STREAMER_MODULE_STATE,
    build_state_map,
)
from app.streamer.process.module.state.helper.pcap_player import PcapPlayer


class StreamerModule(QueueControlProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._storage: Optional[IStorage] = None
        self._storage_root: str = ""
        self._storage_prefix: str = ""
        self._player: Optional[PcapPlayer] = None

    def get_player(self) -> Optional[PcapPlayer]:
        return self._player

    def set_player(self, player: Optional[PcapPlayer]) -> None:
        self._player = player

    def on_init(self):
        super().on_init()
        config = ProjectConfig.instance()
        # Streamer는 downloader가 채운 cache storage를 읽음.
        # raw(원격)는 downloader만 접근하고, streamer는 항상 로컬 cache만 본다.
        self._storage_root = (config.cache_storage_root or "").rstrip("/")
        self._storage_prefix = (config.cache_storage_prefix or "").strip("/")
        self._storage = LocalStorageFactory(LocalStorageInfoFactory()).create_storage()
        self._storage.connect()

        self.set_state_component(
            build_state_map(),
            E_STREAMER_MODULE_STATE.WAIT,
        )

    def get_storage(self) -> Optional[IStorage]:
        return self._storage

    def get_storage_root(self) -> str:
        return self._storage_root

    def get_storage_prefix(self) -> str:
        return self._storage_prefix

    def get_current_state_id(self) -> Optional[E_STREAMER_MODULE_STATE]:
        if self._state_component is None:
            return None
        current = self._state_component.get_state_manager().get_current_state_id()
        if current is None:
            return None
        assert isinstance(current, E_STREAMER_MODULE_STATE)
        return current

    def handle_play_request(self, packet: InrPlayReq) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        if self.get_current_state_id() != E_STREAMER_MODULE_STATE.WAIT:
            self.send_message_rep_inner_queue(
                E_PROTOCOL_ID.INR_PLAY_REP,
                E_CATE.E_STREAMER.E_COMMON.STREAMER_MANAGER,
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if self._state_component is not None:
            self._state_component.change_state(
                E_STREAMER_MODULE_STATE.PLAY,
                state_param_dto=packet,
            )

    def handle_pause_request(self, packet: InrPauseReq) -> None:
        # 어느 state에서든 PAUSE 진입 허용.
        if self._state_component is not None:
            self._state_component.change_state(
                E_STREAMER_MODULE_STATE.PAUSE,
                state_param_dto=packet,
            )

    def handle_seek_request(self, packet: InrSeekReq) -> None:
        # 어느 state에서든 SEEK 진입 허용.
        if self._state_component is not None:
            self._state_component.change_state(
                E_STREAMER_MODULE_STATE.SEEK,
                state_param_dto=packet,
            )

    def handle_close_request(self, packet: InrCloseReq) -> None:
        # 어느 state에서든 CLOSE 진입 허용.
        if self._state_component is not None:
            self._state_component.change_state(
                E_STREAMER_MODULE_STATE.CLOSE,
                state_param_dto=packet,
            )

    def handle_stop_request(self, packet: InrStopReq) -> None:
        # 어느 state에서든 STOP 진입 허용.
        if self._state_component is not None:
            self._state_component.change_state(
                E_STREAMER_MODULE_STATE.STOP,
                state_param_dto=packet,
            )
