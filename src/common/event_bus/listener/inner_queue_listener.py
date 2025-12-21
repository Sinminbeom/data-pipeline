from process.process import abProcess

from src.common.event_bus.listener.listener import abListener


class InnerQueueListener(abListener):
    def __init__(self, parent_process: abProcess) -> None:
        super().__init__(parent_process)

    def action(self) -> None:
        pass

