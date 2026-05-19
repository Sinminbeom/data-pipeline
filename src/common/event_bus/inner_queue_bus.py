from __future__ import annotations

from python_library.logger.app_logger import AppLogger

from common.event_bus.event_bus import abEventBus
from common.event_bus.listener.inner_queue_listener import InnerQueueListener
from common.process.queue_control_process import QueueControlProcess
from protocol.message.message import IMessage, ResponseInfo
from protocol.protocol_wrapper import ProtocolWrapper


class InnerQueueBus(abEventBus[QueueControlProcess]):
    def __init__(self, _parent_process: QueueControlProcess) -> None:
        super().__init__(_parent_process)
        self.listener = InnerQueueListener(_parent_process)

    def send_message_inner_queue(self, receiver_process_name: str, message: str) -> None:
        self._parent_process.push_shared_queue(receiver_process_name, message)

    def _wrap_and_send(self, receiver_process_name: str, packet: IMessage) -> None:
        wrapper = ProtocolWrapper.get_protocol_wrapper(packet)
        envelope = wrapper.get_protocol_packet_message()
        log = AppLogger.instance()
        log.info(f"[INNER_QUEUE SEND] {wrapper.summary(packet)}")
        log.debug(f"[INNER_QUEUE SEND payload] {envelope}")
        self.send_message_inner_queue(receiver_process_name, envelope)

    def send_message_req_inner_queue(
        self,
        protocol_id,
        receiver_process_name: str,
        *args,
    ) -> None:
        from protocol.protocol_meta import ProtocolMeta
        from protocol.protocol_owner import ProtocolOwner

        app_name = self._parent_process.get_app_name()
        sender = ProtocolOwner.build(app_name, self._parent_process.name)
        receiver = ProtocolOwner.build(app_name, receiver_process_name)
        factory = ProtocolMeta.instance().get_protocol_factory(protocol_id)
        packet = factory(sender, receiver, *args)
        self._wrap_and_send(receiver_process_name, packet)

    def broadcast_message_req_inner_queue(
        self,
        protocol_id,
        receiver_process_names: list[str],
        *args,
    ) -> None:
        """동일 REQ를 N개 receiver에 fan-out. 모든 args는 receiver별로 동일하게 전달."""
        for name in receiver_process_names:
            self.send_message_req_inner_queue(protocol_id, name, *args)

    def send_message_rep_inner_queue(
        self,
        protocol_id,
        receiver_process_name: str,
        *args,
        response: ResponseInfo,
    ) -> None:
        from protocol.protocol_meta import ProtocolMeta
        from protocol.protocol_owner import ProtocolOwner

        app_name = self._parent_process.get_app_name()
        sender = ProtocolOwner.build(app_name, self._parent_process.name)
        receiver = ProtocolOwner.build(app_name, receiver_process_name)
        factory = ProtocolMeta.instance().get_protocol_factory(protocol_id)
        packet = factory(sender, receiver, *args, response=response)
        self._wrap_and_send(receiver_process_name, packet)
