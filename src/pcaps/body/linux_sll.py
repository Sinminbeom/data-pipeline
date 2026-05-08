from __future__ import annotations

from pcaps.ipcap import IPCap
from pcaps.pcap_body import abTcpPcapBody, abUdpPcapBody


class UdpLinuxSll(abUdpPcapBody):
    def __init__(self) -> None:
        super().__init__(IPCap.E_LINK_TYPE.LINUX_SLL)

    def get_data_load(self) -> bytes:
        return self.data[44:]

    def parser_pcap(self, data: bytes) -> UdpLinuxSll:
        self.data = data

        self.protocol = int.from_bytes(self._get_data()[25:26], "little")

        binary = self._get_data()[28:28 + 4]
        self.source_address = ".".join(map(str, binary))

        binary = self._get_data()[32:32 + 4]
        self.destination_address = ".".join(map(str, binary))

        self.length = int.from_bytes(self._get_data()[40:40 + 2], "little")
        self.checksum = int.from_bytes(self._get_data()[42:42 + 2], "little")

        return self


class TcpLinuxSll(abTcpPcapBody):
    def __init__(self) -> None:
        super().__init__(IPCap.E_LINK_TYPE.LINUX_SLL)

    def get_data_load(self) -> bytes:
        return self.data[68:]

    def parser_pcap(self, data: bytes) -> TcpLinuxSll:
        self.data = data

        self.protocol = int.from_bytes(self._get_data()[25:26], "little")

        binary = self._get_data()[28:28 + 4]
        self.source_address = ".".join(map(str, binary))

        binary = self._get_data()[32:32 + 4]
        self.destination_address = ".".join(map(str, binary))

        self.length = int.from_bytes(self._get_data()[59:59 + 1], "little")
        self.checksum = int.from_bytes(self._get_data()[52:52 + 2], "little")

        binary = self._get_data()[48:48 + 2]
        ack_and_psh = int.from_bytes(binary[1:], "little") & IPCap.E_TCP_FLAG.ACK_AND_PSH

        self.ack = (ack_and_psh >> 3) & 1
        self.psh = (ack_and_psh >> 4) & 1

        return self
