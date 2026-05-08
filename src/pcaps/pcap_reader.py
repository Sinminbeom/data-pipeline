from __future__ import annotations

from typing import Callable, Optional

from pcaps.ipcap import IPCap
from pcaps.pcap_body import abPcapBody
from pcaps.pcap_dto import PcapDTO
from pcaps.pcap_elements_dto import PcapElementsDTO
from pcaps.pcap_elements_pool import PcapElementsDTOFlagWrapper, PcapElementsPool
from pcaps.pcap_file_header import PcapFileHeader
from pcaps.pcap_packet_header import PcapPacketHeader

FilterFn = Callable[[PcapPacketHeader, abPcapBody], bool]


class PcapReader(IPCap):
    """단일 .pcap 파일 reader — file/packet header + body parse + elements pool 누적."""

    def __init__(self, filter_lambda: Optional[FilterFn] = None) -> None:
        self.pcap_file_header: Optional[PcapFileHeader] = None
        self.elements_pool: PcapElementsPool = PcapElementsPool()
        self.__set_filter(filter_lambda)

    def __set_filter(self, filter_lambda: Optional[FilterFn]) -> None:
        self.filter_lambda: Optional[FilterFn] = filter_lambda

    def __is_filtering(self, pcap_packet_header: PcapPacketHeader, pcap_body: abPcapBody) -> bool:
        if self.filter_lambda is None:
            return False
        return self.filter_lambda(pcap_packet_header, pcap_body)

    def get_elements_pool(self) -> PcapElementsPool:
        return self.elements_pool

    def get_pcap_head_dto(self) -> PcapElementsDTOFlagWrapper:
        return self.elements_pool.get(0)

    def get_pool_size(self) -> int:
        return self.elements_pool.get_size()

    def read_pcap(
        self,
        pcap_file_path: str,
        world_pcap_first_dto: Optional[PcapDTO] = None,
    ) -> PcapReader:
        packet_index = 1
        pcap_dtoed_first: Optional[PcapElementsDTO] = None
        pcap_dtoed: Optional[PcapElementsDTO] = None

        with open(pcap_file_path, "rb") as f:
            self.pcap_file_header = PcapFileHeader.from_file(f)

            while True:
                pcap_packet_header = PcapPacketHeader.from_file(f)
                if pcap_packet_header is None:
                    break

                pcap_body = abPcapBody.from_file(
                    self.pcap_file_header.get_link_type(),
                    pcap_packet_header.get_packet_len(),
                    f,
                )
                if pcap_body is None:
                    break

                pcap_dto = PcapElementsDTO(
                    packet_index,
                    pcap_packet_header,
                    pcap_body,
                    pcap_dtoed_first,
                    pcap_dtoed,
                    world_pcap_first_dto,
                )

                if self.__is_filtering(pcap_packet_header, pcap_body):
                    pass
                else:
                    self.elements_pool.append(pcap_dto)
                    packet_index += 1

                pcap_dtoed = pcap_dto
                if pcap_dtoed_first is None:
                    pcap_dtoed_first = pcap_dto

        return self

    def println(self) -> None:
        self.elements_pool.println()
