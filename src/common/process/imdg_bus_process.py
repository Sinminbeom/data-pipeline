from common.event_bus.imdg_bus import ImdgBus
from common.process.bus_process import BusProcess
from config.project_config import ProjectConfig
from define.define import E_COMMUNICATION_TYPE


class ImdgBusProcess(BusProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)
        self.channel_name = ProjectConfig.instance().channel_name
        self._imdg_bus: ImdgBus | None = None

    def on_init(self):
        super().on_init()
        self._imdg_bus = ImdgBus(self, self.channel_name)
        self._imdg_bus.start()

    def is_ignore(self, communication_type: E_COMMUNICATION_TYPE, receiver: str) -> bool:
        from protocol.protocol_owner import ProtocolOwner
        return not ProtocolOwner.is_owner(receiver, self.get_app_name(), self.name)

    def send_message_imdg(self, _message: str) -> None:
        self._imdg_bus.send_message_imdg_queue(_message)
