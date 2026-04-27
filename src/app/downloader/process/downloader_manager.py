from common.process.imdg_bus_process import IImdgBusProcess, ImdgBusProcess
from protocol.message.message import IMessage
from protocol.protocol_wrapper import ProtocolWrapper


class DownloaderManager(ImdgBusProcess):
    def __init__(self, app_name, process_name):
        super().__init__(app_name, process_name)

    @staticmethod
    def playable_list_request(process: IImdgBusProcess, wrapper: ProtocolWrapper, packet: IMessage):
        pass
