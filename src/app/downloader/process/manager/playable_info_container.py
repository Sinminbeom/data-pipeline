from __future__ import annotations

from protocol.section_element import SectionElement, SectionElementContainer


class PlayableInfoContainer:
    def __init__(self) -> None:
        self._playable_list: list[SectionElement] = []
        self._playable_file_list: dict[str, SectionElementContainer | None] = {}
        self._playable_sensor_ids: set[str] = set()

    def init(self) -> None:
        self._playable_list = []
        self._playable_file_list = {}
        self._playable_sensor_ids = set()

    def get_playable_list(self) -> list[SectionElement]:
        return self._playable_list

    def set_playable_list(self, playable_list: list[SectionElement]) -> None:
        self._playable_list = playable_list

    def get_playable_sensor_ids(self) -> set[str]:
        return self._playable_sensor_ids

    def set_playable_sensor_ids(self, sensor_ids: set[str]) -> None:
        self._playable_sensor_ids = sensor_ids

    def get_playable_file_list(self) -> dict[str, SectionElementContainer | None]:
        return self._playable_file_list

    def set_playable_file_list(self, file_list: dict[str, SectionElementContainer | None]) -> None:
        self._playable_file_list = file_list

    def append_playable_file_list(self, process_id: str, file_list: SectionElementContainer) -> None:
        self._playable_file_list[process_id] = file_list
