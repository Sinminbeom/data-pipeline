from __future__ import annotations

from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

from pcaps.ipcap import IPCap


class abPcapBody(IPCap, ABC):
    """PCAP 패킷 body 추상 — link-type/protocol별 구현은 body/ 하위."""

    def __init__(self, link_type: int, protocol: int) -> None:
        self.data: bytes = b""
        self.protocol: int = protocol
        self.link_type: int = link_type

        self.source_address: str = ""
        self.destination_address: str = ""
        self.length: int = 0
        self.checksum: int = 0

    def _get_data(self) -> bytes:
        return self.data

    def get_data_load(self) -> bytes:
        # 기본 — Ethernet/UDP의 IP+UDP 헤더 42바이트 이후
        return self.data[42:]

    def get_protocol(self) -> int:
        return self.protocol

    def get_source_ipaddr(self) -> str:
        return self.source_address

    def get_destination_ipaddr(self) -> str:
        return self.destination_address

    @abstractmethod
    def parser_pcap(self, data: bytes): ...

    @staticmethod
    def from_file(link_type: int, pak_len: int, file_point: BinaryIO) -> Optional[abPcapBody]:
        from pcaps.body.ethernet import TcpEthernet, UdpEthernet
        from pcaps.body.linux_sll import TcpLinuxSll, UdpLinuxSll
        from pcaps.body.linux_sll_v2 import TcpLinuxSllV2, UdpLinuxSllV2

        if pak_len <= 0:
            return None

        data = file_point.read(pak_len)

        pcap_body: Optional[abPcapBody] = None

        if link_type == IPCap.E_LINK_TYPE.ETHERNET:
            protocol = int.from_bytes(data[23:24], "little")
            pcap_body = UdpEthernet() if protocol == IPCap.E_PROTOCOL.UDP else TcpEthernet()
        elif link_type == IPCap.E_LINK_TYPE.LINUX_SLL:
            protocol = int.from_bytes(data[25:26], "little")
            pcap_body = UdpLinuxSll() if protocol == IPCap.E_PROTOCOL.UDP else TcpLinuxSll()
        elif link_type == IPCap.E_LINK_TYPE.LINUX_SLL_V2:
            protocol = int.from_bytes(data[29:30], "little")
            pcap_body = UdpLinuxSllV2() if protocol == IPCap.E_PROTOCOL.UDP else TcpLinuxSllV2()

        if pcap_body is not None:
            pcap_body.parser_pcap(data)

        return pcap_body


class abTcpPcapBody(abPcapBody, ABC):
    def __init__(self, link_type: int) -> None:
        super().__init__(link_type, IPCap.E_PROTOCOL.TCP)
        self.ack: int = 0
        self.psh: int = 0

    def get_ack(self) -> int:
        return self.ack

    def get_psh(self) -> int:
        return self.psh


class abUdpPcapBody(abPcapBody, ABC):
    def __init__(self, link_type: int) -> None:
        super().__init__(link_type, IPCap.E_PROTOCOL.UDP)
