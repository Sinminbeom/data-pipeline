from python_library.process.process import abProcess

from common.process.queue_control_process import QueueControlProcess
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper


class DownloaderModule(QueueControlProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)
        pass

    @staticmethod
    def playable_list_request(process: abProcess, wrapper: ProtocolWrapper, packet: IMessage):
        pass

    def action(self) -> None:
        pass
