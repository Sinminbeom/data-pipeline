from process.process import abProcess

from src.common.process.bus_process import BusProcess
from src.protocol.message.packet import Packet


class DownloaderManager(BusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        pass

    @staticmethod
    def playable_list_request(process: abProcess, packet: Packet):
        pass

    def action(self) -> None:
        pass

