from python_library.process.process import abProcess

from common.event_bus.event_bus import EventBus
from common.event_bus.listener.inner_queue_listener import InnerQueueListener


class InnerQueueBus(EventBus):
    def __init__(self, _parent_process: abProcess) -> None:
        super().__init__(_parent_process)
        self.listener = InnerQueueListener(_parent_process)

    def send_message_inner_queue(self, receiver_process_name: str, message: str) -> None:
        self._parent_process.push_shared_queue(receiver_process_name, message)

    def send_message_req_inner_queue(
        self,
        protocol_id,
        receiver_process_name: str,
        *args,
    ) -> None:
        from protocol.protocol_meta import ProtocolMeta
        from protocol.protocol_owner import ProtocolOwner
        from protocol.protocol_wrapper import ProtocolWrapper

        app_name = self._parent_process.get_app_name()
        sender = ProtocolOwner.build(app_name, self._parent_process.name)
        receiver = ProtocolOwner.build(app_name, receiver_process_name)
        factory = ProtocolMeta.get_protocol_factory(protocol_id)
        packet = factory(sender, receiver, *args)
        envelope = ProtocolWrapper.get_protocol_wrapper(packet).get_protocol_packet_message()
        self.send_message_inner_queue(receiver_process_name, envelope)
