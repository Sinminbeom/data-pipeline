from process.process import abProcess

from src.common.event_bus.event_bus import EventBus
from src.common.event_bus.listener.inner_queue_listener import InnerQueueListener


class InnerQueueBus(EventBus):
    def __init__(self, _parent_process: abProcess) -> None:
        super().__init__(_parent_process)
        self.listener = InnerQueueListener(_parent_process)


    pass