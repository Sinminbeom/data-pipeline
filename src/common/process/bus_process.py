from src.common.event_bus.imdg_bus import ImdgBus
from src.common.process.queue_control_process import QueueControlProcess


class BusProcess(QueueControlProcess):
    def __init__(self, app_name: str, process_name: str, channel_name: str) -> None:
        super().__init__(app_name, process_name)
        self.channel_name = channel_name
        self._imdg_bus: ImdgBus | None = None

    def on_init(self):
        super().on_init()
        self._imdg_bus = ImdgBus(self, self.channel_name)
        self._imdg_bus.start()
        pass

    def send_message_imdg(self, _message: str) -> None:
        self._imdg_bus.send_message_imdg_queue(_message)