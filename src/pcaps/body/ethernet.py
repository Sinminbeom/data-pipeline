from __future__ import annotations

from pcaps.ipcap import IPCap
from pcaps.pcap_body import abTcpPcapBody, abUdpPcapBody


class UdpEthernet(abUdpPcapBody):
    def __init__(self) -> None:
        super().__init__(IPCap.E_LINK_TYPE.ETHERNET)

    def parser_pcap(self, data: bytes) -> UdpEthernet:
        self.data = data

        self.protocol = int.from_bytes(self._get_data()[23:24], "little")

        binary = self._get_data()[26:26 + 4]
        self.source_address = ".".join(map(str, binary))

        binary = self._get_data()[30:30 + 4]
        self.destination_address = ".".join(map(str, binary))

        self.length = int.from_bytes(self._get_data()[39:39 + 2], "little")
        self.checksum = int.from_bytes(self._get_data()[40:40 + 2], "little")

        return self


class TcpEthernet(abTcpPcapBody):
    def __init__(self) -> None:
        super().__init__(IPCap.E_LINK_TYPE.ETHERNET)

    def get_data_load(self) -> bytes:
        return self.data[66:]

    def parser_pcap(self, data: bytes) -> TcpEthernet:
        self.data = data

        self.protocol = int.from_bytes(self._get_data()[23:24], "little")

        binary = self._get_data()[26:26 + 4]
        self.source_address = ".".join(map(str, binary))

        binary = self._get_data()[30:30 + 4]
        self.destination_address = ".".join(map(str, binary))

        self.length = int.from_bytes(self._get_data()[57:57 + 1], "little")
        self.checksum = int.from_bytes(self._get_data()[50:50 + 2], "little")

        binary = self._get_data()[46:46 + 2]
        ack_and_psh = int.from_bytes(binary[1:], "little") & IPCap.E_TCP_FLAG.ACK_AND_PSH

        self.ack = (ack_and_psh >> 3) & 1
        self.psh = (ack_and_psh >> 4) & 1

        return self
