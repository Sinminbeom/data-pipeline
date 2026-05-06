from typing import Mapping

from common.event_bus.inner_queue_bus import InnerQueueBus
from common.process.step_process import StepProcess
from protocol.message.message import ResponseInfo
from protocol.protocol_meta import E_PROTOCOL_ID, ReceiverKey, HandlerFn


class QueueControlProcess(StepProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(app_name, process_name)

        self._inner_queue_bus = None
        self._handler: dict[E_PROTOCOL_ID, Mapping[ReceiverKey, HandlerFn]] | None = None

    def on_init(self):
        self._inner_queue_bus=InnerQueueBus(self)
        self._inner_queue_bus.start()
        pass

    def on_register_handler(self, handler: dict[E_PROTOCOL_ID, Mapping[ReceiverKey, HandlerFn]]):
        self._handler = handler
        pass

    def send_message_inner_queue(self, receiver_process_name: str, message: str) -> None:
        assert self._inner_queue_bus is not None
        self._inner_queue_bus.send_message_inner_queue(receiver_process_name, message)

    def send_message_req_inner_queue(
        self,
        protocol_id,
        receiver_process_name: str,
        *args,
    ) -> None:
        assert self._inner_queue_bus is not None
        self._inner_queue_bus.send_message_req_inner_queue(protocol_id, receiver_process_name, *args)

    def send_message_rep_inner_queue(
        self,
        protocol_id,
        receiver_process_name: str,
        *args,
        response: ResponseInfo,
    ) -> None:
        assert self._inner_queue_bus is not None
        self._inner_queue_bus.send_message_rep_inner_queue(
            protocol_id, receiver_process_name, *args, response=response
        )

    def on_proc_once(self):
        pass

    def on_proc_every_frame(self):
        pass
