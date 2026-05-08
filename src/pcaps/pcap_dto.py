from pcaps.ipcap_dto import IPCapDTO


class PcapDTO(IPCapDTO):
    """PcapElementsDTO에서 핵심 timestamp 정보만 추출한 단순 DTO."""

    def __init__(
        self,
        no: int,
        time_stamp: float,
        time_stamp_str: str,
        offset_time: float,
        accumulate_offset_time: float,
    ) -> None:
        self.no: int = no
        self.time_stamp: float = time_stamp
        self.time_stamp_str: str = time_stamp_str
        self.offset_time: float = offset_time
        self.accumulate_offset_time: float = accumulate_offset_time

    def get_time_stamp(self) -> float:
        return self.time_stamp

    def get_time_str(self) -> str:
        return self.time_stamp_str

    def get_offset_time_stamp(self) -> float:
        return self.offset_time

    def get_accumulate_offset_time_stamp(self) -> float:
        return self.accumulate_offset_time

    def get_no(self) -> int:
        return self.no

    def get_data_payload(self) -> bytes:
        return b""
