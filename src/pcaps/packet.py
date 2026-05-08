from __future__ import annotations

from dataclasses import dataclass

from pcaps.body.pcap_body import abPcapBody
from pcaps.headers.packet_header import PacketHeader
from pcaps.time_info import TimeInfo


@dataclass(frozen=True)
class PcapPacket:
    """PCAP 한 패킷 — header + body + 시간 정보."""
    no: int
    header: PacketHeader
    body: abPcapBody
    time: TimeInfo

    @property
    def payload(self) -> bytes:
        return self.body.payload
