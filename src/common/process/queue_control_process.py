from src.common.event_bus.inner_queue_bus import InnerQueueBus
from src.common.process.step_process import StepProcess


class QueueControlProcess(StepProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)

        self._innerQueueBus = None
        self._handler = None

    def on_init(self):

        self._innerQueueBus=InnerQueueBus(self)
        self._innerQueueBus.start()
        pass

    def on_proc_once(self):
        pass

    def on_proc_every_frame(self):
        pass

