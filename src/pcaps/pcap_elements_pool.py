from pcaps.ipcap import IDTO
from pcaps.pcap_elements_dto import PcapElementsDTO


class PcapElementsDTOFlagWrapper(IDTO):
    """active flag를 가진 PcapElementsDTO wrapper — Pool에 보관."""

    def __init__(self, pcap_elements_dto: PcapElementsDTO) -> None:
        super().__init__()
        self.pcap_elements_dto: PcapElementsDTO = pcap_elements_dto
        self.__set_active(True)

    def __set_active(self, active: bool) -> None:
        self.active: bool = active

    def get_elements_dto(self) -> PcapElementsDTO:
        return self.pcap_elements_dto

    def set_active(self, active: bool) -> None:
        self.__set_active(active)

    def is_active(self) -> bool:
        return self.active

    def to_string(self) -> str:
        return f"""Active: {self.is_active()} {self.pcap_elements_dto.to_string()} """


class PcapElementsPool:
    """패킷 단위 PcapElementsDTO 누적 보관 + active flag 관리 pool."""

    def __init__(self) -> None:
        self.pool: list[PcapElementsDTOFlagWrapper] = []

    def append(self, dto: PcapElementsDTO) -> None:
        self.pool.append(PcapElementsDTOFlagWrapper(dto))

    def get(self, index: int) -> PcapElementsDTOFlagWrapper:
        return self.pool[index]

    def get_pool(self) -> list[PcapElementsDTOFlagWrapper]:
        return self.pool

    def get_size(self) -> int:
        return len(self.pool)

    def __get_active_buffer_index(self) -> int:
        """이진 탐색 — active=False가 앞에서부터 채워질 때 첫 active=True 인덱스."""
        left, right = 0, len(self.pool) - 1

        while left <= right:
            mid = (left + right) // 2

            if self.pool[mid].is_active() and (mid == 0 or self.pool[mid - 1].is_active() is False):
                return mid

            if self.pool[mid].is_active():
                right = mid - 1
            else:
                left = mid + 1
        return -1

    def __get_active_buffer(self) -> None:
        ind = self.__get_active_buffer_index()
        print(f"ind:{ind}")

    def pop_with_time_stamp(self, accumulate_offset_time: float) -> None:
        self.__get_active_buffer()

    def println(self) -> None:
        for dto in self.pool:
            elements = dto.get_elements_dto()
            print(
                f" N : {elements.get_no():>5} "
                f" ts : {elements.get_time_str()}  "
                f" t:{elements.get_time_stamp():<20} "
                f" of : {elements.get_offset_time_stamp():<22} "
                f" auof : {elements.get_accumulate_offset_time_stamp()} "
                f" w_auof : {elements.get_world_accumulate_offset_time_stamp()} "
                f" dpayload_size:{len(elements.get_data_payload())}"
            )
