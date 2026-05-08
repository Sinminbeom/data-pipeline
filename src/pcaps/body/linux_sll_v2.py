from __future__ import annotations

from pcaps.ipcap import IPCap
from pcaps.pcap_body import abTcpPcapBody, abUdpPcapBody


class UdpLinuxSllV2(abUdpPcapBody):
    def __init__(self) -> None:
        # replayer 원본은 LINUX_SLL을 그대로 link_type으로 둠 — 동일 보존.
        super().__init__(IPCap.E_LINK_TYPE.LINUX_SLL)

    def get_data_load(self) -> bytes:
        return self.data[48:]

    def parser_pcap(self, data: bytes) -> UdpLinuxSllV2:
        self.data = data

        self.protocol = int.from_bytes(self._get_data()[29:29 + 1], "little")

        binary = self._get_data()[32:32 + 4]
        self.source_address = ".".join(map(str, binary))

        binary = self._get_data()[36:36 + 4]
        self.destination_address = ".".join(map(str, binary))

        self.length = int.from_bytes(self._get_data()[44:44 + 2], "little")
        self.checksum = int.from_bytes(self._get_data()[46:46 + 2], "little")

        return self


class TcpLinuxSllV2(abTcpPcapBody):
    def __init__(self) -> None:
        super().__init__(IPCap.E_LINK_TYPE.LINUX_SLL)

    def get_data_load(self) -> bytes:
        return self.data[68:]

    def parser_pcap(self, data: bytes) -> TcpLinuxSllV2:
        self.data = data

        self.protocol = int.from_bytes(self._get_data()[25:26], "little")

        binary = self._get_data()[28:28 + 4]
        self.source_address = ".".join(map(str, binary))

        binary = self._get_data()[32:32 + 4]
        self.destination_address = ".".join(map(str, binary))

        self.length = int.from_bytes(self._get_data()[63:63 + 1], "little")
        self.checksum = int.from_bytes(self._get_data()[56:56 + 2], "little")

        binary = self._get_data()[52:52 + 2]
        ack_and_psh = int.from_bytes(binary[1:], "little") & IPCap.E_TCP_FLAG.ACK_AND_PSH

        self.ack = (ack_and_psh >> 3) & 1
        self.psh = (ack_and_psh >> 4) & 1

        return self
