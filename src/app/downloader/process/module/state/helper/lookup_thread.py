from __future__ import annotations

from datetime import datetime, timedelta

from python_library.storage.storage import IStorage
from python_library.thread.thread import abThread

from protocol.section_element import SectionElement, SectionElementContainer


MINUTE_FORMAT = "%Y%m%d%H%M"


class LookupThread(abThread):
    def __init__(
        self,
        storage: IStorage,
        storage_root: str,
        storage_prefix: str,
        vehicle_id: str,
        sensor_id: str,
        category: str,
        start_time: str,
        end_time: str,
    ) -> None:
        super().__init__()
        self._storage = storage
        self._storage_root = storage_root
        self._storage_prefix = storage_prefix
        self._vehicle_id = vehicle_id
        self._sensor_id = sensor_id
        self._category = category
        self._start_time = start_time
        self._end_time = end_time

        self._sections: list[SectionElement] = []
        self._error: Exception | None = None

    def action(self) -> None:
        try:
            base_path = self.__build_base_path()
            timestamps = self.__collect_timestamps(base_path)
            self._sections = SectionElementContainer.calculate_intersection(sorted(timestamps))
        except Exception as e:
            self._error = e

    def get_sections(self) -> list[SectionElement]:
        return self._sections

    def get_error(self) -> Exception | None:
        return self._error

    def __build_base_path(self) -> str:
        parts = [self._storage_prefix, self._vehicle_id, self._category, self._sensor_id.lower()]
        suffix = "/".join(p for p in parts if p)
        return f"{self._storage_root}/{suffix}"

    def __collect_timestamps(self, base_path: str) -> set[str]:
        results: set[str] = set()
        cursor = datetime.strptime(self._start_time[:12], MINUTE_FORMAT)
        end_minute = datetime.strptime(self._end_time[:12], MINUTE_FORMAT)

        while cursor <= end_minute:
            minute_path = self.__build_minute_path(base_path, cursor)
            for storage_file in self._storage.get_file_list(minute_path):
                if storage_file.is_dir():
                    continue
                ts = storage_file.get_file_name().split(".")[0][-14:]
                if len(ts) != 14 or not ts.isdigit():
                    continue
                if self._start_time <= ts <= self._end_time:
                    results.add(ts)
            cursor += timedelta(minutes=1)
        return results

    @staticmethod
    def __build_minute_path(base_path: str, when: datetime) -> str:
        return f"{base_path}/{when.strftime('%Y%m%d')}/{when.strftime('%H')}/{when.strftime('%M')}/"
