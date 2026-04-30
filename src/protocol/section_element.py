from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SectionElement:
    section_id: int
    start_time: str
    end_time: str

    def get_section_id(self) -> int:
        return self.section_id

    def get_start_time(self) -> str:
        return self.start_time

    def get_end_time(self) -> str:
        return self.end_time


class SectionElementContainer:
    TIME_FORMAT = "%Y%m%d%H%M%S"

    def __init__(self, section_element_list: list[SectionElement] | None = None) -> None:
        self._section_element_list: list[SectionElement] = (
            section_element_list if section_element_list is not None else []
        )

    def get_section_element_list(self) -> list[SectionElement]:
        return self._section_element_list

    def append(self, section_element: SectionElement) -> None:
        self._section_element_list.append(section_element)

    def convert_one_dimensional_list(self) -> list[str]:
        if not self._section_element_list:
            return []

        result: list[str] = []
        for elem in self._section_element_list:
            start = datetime.strptime(elem.get_start_time(), self.TIME_FORMAT)
            end = datetime.strptime(elem.get_end_time(), self.TIME_FORMAT)
            current = start
            while current <= end:
                result.append(current.strftime(self.TIME_FORMAT))
                current += timedelta(seconds=1)
        return result

    @staticmethod
    def calculate_intersection(*one_dim_lists: list[str]) -> list[SectionElement]:
        if not one_dim_lists:
            return []

        intersection_set: set[str] = set(one_dim_lists[0])
        for lst in one_dim_lists[1:]:
            intersection_set &= set(lst)

        return SectionElementContainer._find_playable_period(sorted(intersection_set))

    @staticmethod
    def _find_playable_period(sorted_times: list[str]) -> list[SectionElement]:
        if not sorted_times:
            return []

        result: list[SectionElement] = []
        section_index = 0
        cur_sub: list[str] = [sorted_times[0]]

        for i in range(1, len(sorted_times)):
            if SectionElementContainer._is_diff_one_sec(sorted_times[i], sorted_times[i - 1]):
                cur_sub.append(sorted_times[i])
            else:
                result.append(SectionElement(section_index, cur_sub[0], cur_sub[-1]))
                section_index += 1
                cur_sub = [sorted_times[i]]

        result.append(SectionElement(section_index, cur_sub[0], cur_sub[-1]))
        return result

    @staticmethod
    def _is_diff_one_sec(time1: str, time2: str) -> bool:
        dt1 = datetime.strptime(time1, SectionElementContainer.TIME_FORMAT)
        dt2 = datetime.strptime(time2, SectionElementContainer.TIME_FORMAT)
        return abs((dt2 - dt1).total_seconds()) == 1
