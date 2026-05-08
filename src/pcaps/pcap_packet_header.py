from __future__ import annotations

import datetime
from typing import BinaryIO, Optional

from pcaps.ipcap import IPCap


class PcapPacketHeader(IPCap):
    """PCAP 패킷별 16바이트 헤더 — captime/caputime/caplen/packlen."""

    def __init__(self) -> None:
        self.captime: int = 0       # uint, second
        self.caputime: int = 0      # uint, microsecond
        self.caplen: int = 0        # uint
        self.packlen: int = 0       # uint

    @staticmethod
    def from_file(file_point: BinaryIO) -> Optional[PcapPacketHeader]:
        binary = file_point.read(4)

        if not binary:
            return None

        header = PcapPacketHeader()
        header.captime = int.from_bytes(binary, "little")

        binary = file_point.read(4)
        header.caputime = int.from_bytes(binary, "little")

        binary = file_point.read(4)
        header.caplen = int.from_bytes(binary, "little")

        binary = file_point.read(4)
        header.packlen = int.from_bytes(binary, "little")

        return header

    def get_time_stamp(self) -> float:
        return self.captime + self.caputime / 1e6

    def get_time_str(self) -> str:
        timestamp = self.captime + self.caputime / 1e6
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")

    def get_packet_len(self) -> int:
        return self.packlen
