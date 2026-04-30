from __future__ import annotations

from typing import TYPE_CHECKING

from python_library.state import abState

from protocol.message.imdg.playable_list import PlayableListReq
from protocol.section_element import SectionElementContainer

if TYPE_CHECKING:
    from app.downloader.process.manager.manager import DownloaderManager


class PlayableState(abState):
    owner: DownloaderManager

    def on_enter(self):
        assert isinstance(self.state_param_dto, PlayableListReq)
        sensor_ids = set(self.state_param_dto.sensor_id_list)
        self.owner.set_playable_sensor_ids(sensor_ids)
        self.owner.init_playable_file_map(sensor_ids)

    def on_leave(self): pass

    def on_proc_once(self):
        from protocol.protocol_meta import E_PROTOCOL_ID

        assert isinstance(self.state_param_dto, PlayableListReq)
        for sensor_id in self.state_param_dto.sensor_id_list:
            self.owner.send_message_req_inner_queue(
                E_PROTOCOL_ID.INR_PLAYABLE_LIST_REQ,
                sensor_id,
                self.state_param_dto.vehicle_id,
                self.state_param_dto.start_time,
                self.state_param_dto.end_time,
            )

    def on_proc_every_frame(self):
        if not self.__is_progress():
            return

        from process_category.enum_category import E_CATE
        from protocol.protocol_code import E_CODE, make_response_info
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner

        from app.downloader.process.manager.state import E_DOWNLOADER_MANAGER_STATE

        self.__calculate_playable_period()
        self.owner.send_message_rep_imdg(
            E_PROTOCOL_ID.PLAYABLE_LIST_REP,
            ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
            list(self.owner.get_playable_sensor_ids()),
            self.owner.get_playable_list(),
            response=make_response_info(E_CODE.OK),
        )

        if self.owner._state_component is not None:
            self.owner._state_component.change_state(E_DOWNLOADER_MANAGER_STATE.DOWNLOAD_READY)

    def __is_progress(self) -> bool:
        file_list = self.owner.get_playable_file_list()
        for sensor_id in self.owner.get_playable_sensor_ids():
            if file_list.get(sensor_id) is None:
                return False
        return True

    def __calculate_playable_period(self) -> None:
        elements_dict = self.owner.get_playable_file_list()
        one_dim_lists: list[list[str]] = []
        for elements in elements_dict.values():
            if isinstance(elements, SectionElementContainer):
                one_dim_lists.append(elements.convert_one_dimensional_list())

        playable_list = SectionElementContainer.calculate_intersection(*one_dim_lists)
        self.owner.set_playable_list(playable_list)
