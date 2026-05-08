from __future__ import annotations

from typing import Optional

from pcaps.ipcap_dto import IPCapDTO
from pcaps.pcap_body import abPcapBody
from pcaps.pcap_dto import PcapDTO
from pcaps.pcap_packet_header import PcapPacketHeader


class PcapElementsDTO(IPCapDTO):
    """패킷 1개에 대한 종합 DTO — header/body + 시간 오프셋 계산 보존."""

    def __init__(
        self,
        no: int,
        pcap_packet_header: Optional[PcapPacketHeader],
        packet_body: Optional[abPcapBody],
        packet_dtoed_first: Optional[PcapElementsDTO] = None,
        packet_dtoed: Optional[PcapElementsDTO] = None,
        world_pcap_first_dto: Optional[PcapDTO] = None,
    ) -> None:
        self.no: int = no
        if pcap_packet_header is None or packet_body is None:
            return

        self.time_stamp: float = pcap_packet_header.get_time_stamp()
        self.data_payload: bytes = packet_body.get_data_load()

        self.packet_header: PcapPacketHeader = pcap_packet_header
        self.packet_body: abPcapBody = packet_body

        self.offset_time: float = 0.0
        self.__set_offset_timestamp(packet_dtoed)

        self.accumulate_offset_time: float = 0.0
        self.__set_accumulate_offset_timestamp(packet_dtoed_first)

        self.world_accumulate_offset_time: float = 0.0
        self.__set_world_accumulate_offset_timestamp(world_pcap_first_dto)

    def get_time_stamp(self) -> float:
        return self.time_stamp

    def get_time_stamp_ns(self) -> float:
        return self.time_stamp * 1_000_000_000

    def get_time_str(self) -> str:
        return self.packet_header.get_time_str()

    def get_offset_time_stamp(self) -> float:
        return self.offset_time

    def get_offset_time_stamp_ns(self) -> float:
        return self.offset_time * 1_000_000_000

    def get_accumulate_offset_time_stamp(self) -> float:
        return self.accumulate_offset_time

    def get_accumulate_offset_time_stamp_ns(self) -> float:
        return self.accumulate_offset_time * 1_000_000_000

    def get_world_accumulate_offset_time_stamp(self) -> float:
        return self.world_accumulate_offset_time

    def get_world_accumulate_offset_time_stamp_ns(self) -> float:
        return self.world_accumulate_offset_time * 1_000_000_000

    def get_no(self) -> int:
        return self.no

    def get_data_payload(self) -> bytes:
        return self.data_payload

    def get_pcap_dto(self) -> PcapDTO:
        return PcapDTO(
            self.no,
            self.get_time_stamp(),
            self.get_time_str(),
            self.get_offset_time_stamp(),
            self.get_accumulate_offset_time_stamp(),
        )

    def __set_world_accumulate_offset_timestamp(self, world_pcap_first_dto: Optional[PcapDTO]) -> None:
        if world_pcap_first_dto is None:
            self.world_accumulate_offset_time = self.accumulate_offset_time
        else:
            self.world_accumulate_offset_time = self.get_time_stamp() - world_pcap_first_dto.get_time_stamp()

    def __set_accumulate_offset_timestamp(self, packet_dtoed_first: Optional[PcapElementsDTO]) -> None:
        if packet_dtoed_first is None:
            self.accumulate_offset_time = 0.0
            return
        self.accumulate_offset_time = self.get_time_stamp() - packet_dtoed_first.get_time_stamp()

    def __set_offset_timestamp(self, packet_dtoed: Optional[PcapElementsDTO]) -> None:
        if packet_dtoed is None:
            self.offset_time = 0.0
            return
        self.offset_time = self.get_time_stamp() - packet_dtoed.get_time_stamp()

    def to_string(self) -> str:
        return (
            f""" no : {self.no}
        time_stamp : {self.time_stamp}
        offset_time: {self.offset_time}
        accumulate_offset_time: {self.accumulate_offset_time}
        world_accumulate_offset_time: {self.world_accumulate_offset_time}
"""
        )
