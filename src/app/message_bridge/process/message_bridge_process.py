from process.process import abProcess

from src.common.process.bus_process import BusProcess
from src.config.project_config import ProjectConfig
from src.protocol.message.packet import Packet
from src.protocol.protocol_wrapper import ProtocolWrapper


class MessageBridgeProcess(BusProcess):
    def __init__(self, app_name, process_name):
        channel_name = ProjectConfig.instance().channel_name
        super().__init__(app_name, process_name, channel_name)
        pass

    @staticmethod
    def playable_list_request(process: abProcess, wrapper: ProtocolWrapper, packet: Packet):
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        pass

    def action(self) -> None:
        pass

