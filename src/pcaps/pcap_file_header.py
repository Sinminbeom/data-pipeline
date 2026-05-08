from __future__ import annotations

from typing import BinaryIO

from pcaps.ipcap import IPCap


class PcapFileHeader(IPCap):
    """PCAP 파일 24바이트 헤더."""

    def __init__(self) -> None:
        self.magic: bytes = b""              # uint, 0xA1B2C3D4
        self.major: int = 0                  # ushort
        self.minor: int = 0                  # ushort
        self.gmt_to_local: int = 0           # uint
        self.timestamp: int = 0              # uint
        self.max_caplen: int = 0             # uint
        self.linktype: int = 0               # uint

    def get_link_type(self) -> int:
        return self.linktype

    @staticmethod
    def from_file(file_point: BinaryIO) -> PcapFileHeader:
        header = PcapFileHeader()

        header.magic = file_point.read(4)

        binary = file_point.read(2)
        header.major = int.from_bytes(binary, "little")

        binary = file_point.read(2)
        header.minor = int.from_bytes(binary, "little")

        binary = file_point.read(4)
        header.gmt_to_local = int.from_bytes(binary, "little")

        binary = file_point.read(4)
        header.timestamp = int.from_bytes(binary, "little")

        binary = file_point.read(4)
        header.max_caplen = int.from_bytes(binary, "little")

        binary = file_point.read(4)
        header.linktype = int.from_bytes(binary, "little")

        return header
