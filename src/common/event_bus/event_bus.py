from process.process import abProcess

from src.common.event_bus.listener.listener import abListener


class EventBus:
    def __init__(self, _parent_process: abProcess) -> None:
        self._parent_process: abProcess = _parent_process
        self.listener: abListener | None = None

    def start(self):
        self.listener.start()