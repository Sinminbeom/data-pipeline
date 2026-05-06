from __future__ import annotations

from typing import Optional

from common.process.imdg_bus_process import ImdgBusProcess
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper
from protocol.section_element import SectionElement, SectionElementContainer

from app.downloader.process.manager.playable_info_container import PlayableInfoContainer
from app.downloader.process.manager.state import (
    E_DOWNLOADER_MANAGER_STATE,
    build_state_map,
)


class DownloaderManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        self._playable_infos = PlayableInfoContainer()

    def on_init(self):
        super().on_init()
        self.set_state_component(
            build_state_map(),
            E_DOWNLOADER_MANAGER_STATE.WAIT,
        )

    def get_current_state_id(self) -> Optional[E_DOWNLOADER_MANAGER_STATE]:
        if self._state_component is None:
            return None
        current = self._state_component.get_state_manager().get_current_state_id()
        if current is None:
            return None
        assert isinstance(current, E_DOWNLOADER_MANAGER_STATE)
        return current

    def get_playable_sensor_ids(self) -> set[str]:
        return self._playable_infos.get_playable_sensor_ids()

    def set_playable_sensor_ids(self, sensor_ids: set[str]) -> None:
        self._playable_infos.set_playable_sensor_ids(sensor_ids)

    def init_playable_file_map(self, sensor_ids: set[str]) -> None:
        file_map: dict[str, SectionElementContainer | None] = {sensor_id: None for sensor_id in sensor_ids}
        self._playable_infos.set_playable_file_list(file_map)

    def get_playable_file_list(self) -> dict[str, SectionElementContainer | None]:
        return self._playable_infos.get_playable_file_list()

    def append_playable_file(self, process_id: str, file_list: SectionElementContainer) -> None:
        self._playable_infos.append_playable_file_list(process_id, file_list)

    def get_playable_list(self) -> list[SectionElement]:
        return self._playable_infos.get_playable_list()

    def set_playable_list(self, playable_list: list[SectionElement]) -> None:
        self._playable_infos.set_playable_list(playable_list)

    @staticmethod
    def playable_list_request(process: DownloaderManager, wrapper: ProtocolWrapper, packet: IMessage):
        from process_category.enum_category import E_CATE
        from protocol.protocol_meta import E_PROTOCOL_ID
        from protocol.protocol_owner import ProtocolOwner
        from protocol.protocol_code import E_CODE, make_response_info

        if process.get_current_state_id() != E_DOWNLOADER_MANAGER_STATE.WAIT:
            process.send_message_rep_imdg(
                E_PROTOCOL_ID.PLAYABLE_LIST_REP,
                ProtocolOwner.build(E_CATE.MESSAGE_BRIDGE, E_CATE.E_MESSAGE_BRIDGE.E_COMMON.MESSAGE_BRIDGE),
                None,
                None,
                response=make_response_info(E_CODE.INVALID_REQUEST),
            )
            return

        if process._state_component is not None:
            process._state_component.change_state(E_DOWNLOADER_MANAGER_STATE.PLAYABLE, state_param_dto=packet)

    @staticmethod
    def playable_list_response(process: DownloaderManager, wrapper: ProtocolWrapper, packet: IMessage):
        from protocol.message.process.playable_list import InrPlayableListRep

        assert isinstance(packet, InrPlayableListRep)

        if process.get_current_state_id() != E_DOWNLOADER_MANAGER_STATE.PLAYABLE:
            return

        elements: list[SectionElement] = []
        for raw in packet.section_list:
            if isinstance(raw, SectionElement):
                elements.append(raw)
            elif isinstance(raw, dict):
                elements.append(SectionElement(**raw))
        container = SectionElementContainer(elements)
        process.append_playable_file(packet.sensor_id, container)
