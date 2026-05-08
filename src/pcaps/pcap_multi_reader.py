from typing import Optional

from pcaps.ipcap import IPCap
from pcaps.pcap_dto import PcapDTO
from pcaps.pcap_reader import FilterFn, PcapReader


class PcapMultiReader(IPCap):
    """여러 .pcap 파일을 순차 read하면서 첫 파일 첫 패킷 시각을 기준점으로 보존.

    Streamer가 여러 sensor의 .pcap을 동기화 재생할 때 활용.
    """

    def __init__(self) -> None:
        self.first_pcap_dto: Optional[PcapDTO] = None

    def reset(self) -> None:
        self.first_pcap_dto = None

    def __upsert_first_dto(self, pcap_reader: PcapReader) -> None:
        if self.first_pcap_dto is None:
            elements_dto = pcap_reader.get_pcap_head_dto().get_elements_dto()
            self.first_pcap_dto = PcapDTO(
                elements_dto.get_no(),
                elements_dto.get_time_stamp(),
                elements_dto.get_time_str(),
                elements_dto.get_offset_time_stamp(),
                elements_dto.get_accumulate_offset_time_stamp(),
            )

    def pcap_read(self, pcap_file_path: str, filter_lambda: Optional[FilterFn] = None) -> PcapReader:
        reader = PcapReader(filter_lambda)
        reader.read_pcap(pcap_file_path, self.first_pcap_dto)

        self.__upsert_first_dto(reader)

        return reader
