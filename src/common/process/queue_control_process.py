from typing import Mapping

from src.common.event_bus.inner_queue_bus import InnerQueueBus
from src.common.process.step_process import StepProcess
from src.protocol.protocol_meta import E_PROTOCOL_ID, ReceiverKey, HandlerFn


class QueueControlProcess(StepProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)

        self._innerQueueBus = None
        self._handler: dict[E_PROTOCOL_ID, Mapping[ReceiverKey, HandlerFn]] | None = None

    def on_init(self):
        self._innerQueueBus=InnerQueueBus(self)
        self._innerQueueBus.start()
        pass

    def on_register_handler(self, handler: dict[E_PROTOCOL_ID, Mapping[ReceiverKey, HandlerFn]]):
        self._handler = handler
        pass

    def on_proc_once(self):
        pass

    def on_proc_every_frame(self):
        pass

