from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from python_library.state import abState

from protocol.message.process.playable_list import InrPlayableListReq
from protocol.section_element import SectionElement

from app.downloader.process.module.state.helper.lookup_thread import LookupThread

if TYPE_CHECKING:
    from app.downloader.process.module.module import DownloaderModule


class PlayableState(abState):
    owner: DownloaderModule

    def __init__(self, state_lists, state_id):  # noqa: D401
        super().__init__(state_lists, state_id)
        self._lookup_thread: Optional[LookupThread] = None

    def on_enter(self):
        assert isinstance(self.state_param_dto, InrPlayableListReq)
        self._lookup_thread = None

    def on_leave(self):
        self._lookup_thread = None

    def on_proc_once(self):
        from sensor_category.sensor_category import SensorCategory

        assert isinstance(self.state_param_dto, InrPlayableListReq)
        sensor_id = self.owner.name
        category = SensorCategory.get(sensor_id)

        if category is None:
            self.__send_invalid_request(sensor_id)
            self.__transition_to_wait()
            return

        storage = self.owner.get_storage()
        assert storage is not None

        self._lookup_thread = LookupThread(
            storage=storage,
            storage_root=self.owner.get_storage_root(),
            storage_prefix=self.owner.get_storage_prefix(),
            vehicle_id=self.state_param_dto.vehicle_id,
            sensor_id=sensor_id,
            category=category,
            start_time=self.state_param_dto.start_time,
            end_time=self.state_param_dto.end_time,
        )
        self._lookup_thread.start()

    def on_proc_every_frame(self):
        if self._lookup_thread is None:
            return
        if self._lookup_thread.is_alive():
            return  # lookup 진행 중

        sensor_id = self.owner.name
        if self._lookup_thread.get_error() is not None:
            self.__send_error(sensor_id, str(self._lookup_thread.get_error()))
            self.__transition_to_wait()
        else:
            self.__send_ok(sensor_id, self._lookup_thread.get_sections())
            self.__transition_to_download_ready()

    def __send_ok(self, sensor_id: str, sections: list[SectionElement]) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_PLAYABLE_LIST_REP,
            E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
            sensor_id,
            sections,
            response=make_response_info(E_CODE.OK),
        )

    def __send_invalid_request(self, sensor_id: str) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_PLAYABLE_LIST_REP,
            E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
            sensor_id,
            [],
            response=make_response_info(E_CODE.INVALID_REQUEST),
        )

    def __send_error(self, sensor_id: str, reason: str) -> None:
        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID

        self.owner.send_message_rep_inner_queue(
            E_PROTOCOL_ID.INR_PLAYABLE_LIST_REP,
            E_CATE.E_DOWNLOADER.E_COMMON.DOWNLOAD_MANAGER,
            sensor_id,
            [],
            response=make_response_info(E_CODE.INVALID_REQUEST, reason=reason),
        )

    def __transition_to_wait(self) -> None:
        from app.downloader.process.module.state.state_enum import E_DOWNLOADER_MODULE_STATE

        self.owner._state_component.change_state(E_DOWNLOADER_MODULE_STATE.WAIT)

    def __transition_to_download_ready(self) -> None:
        from app.downloader.process.module.state.state_enum import E_DOWNLOADER_MODULE_STATE

        self.owner._state_component.change_state(E_DOWNLOADER_MODULE_STATE.DOWNLOAD_READY)
