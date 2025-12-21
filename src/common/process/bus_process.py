from src.common.event_bus.imdg_bus import ImdgBus
from src.common.process.queue_control_process import QueueControlProcess


class BusProcess(QueueControlProcess):
    def __init__(self, app_name: str, process_name: str, channel_name: str) -> None:
        super().__init__(app_name, process_name)
        self._channel_name = channel_name
        self._imdg_bus: ImdgBus | None = None

    def on_init(self):
        self._imdg_bus = ImdgBus(self, self._channel_name)
        pass