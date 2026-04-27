from python_library.process.process import abProcess

from common.process.queue_control_process import QueueControlProcess
from protocol.message.packet import IPacket
from protocol.protocol_wrapper import ProtocolWrapper


class DownloaderModule(QueueControlProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        pass

    @staticmethod
    def playable_list_request(process: abProcess, wrapper: ProtocolWrapper, packet: IPacket):
        pass

    def action(self) -> None:
        pass

