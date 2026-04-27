import redis
from redis.client import Redis, PubSub

from python_library.process.process import abProcess

from common.event_bus.event_bus import EventBus
from common.event_bus.listener.imdg_listener import ImdgListener
from config.project_config import ProjectConfig
from protocol.message.message import ResponseInfo


class ImdgBus(EventBus):
    def __init__(self, _parent_process: abProcess, _channel_name: str) -> None:
        super().__init__(_parent_process)
        self._channel_name = _channel_name

        config = ProjectConfig.instance()
        self._imdg: Redis = redis.StrictRedis(host=config.server_ip, port=int(config.server_port))

        self._pubsub: PubSub = self._imdg.pubsub()
        self._pubsub.subscribe(self._channel_name)
        self.listener = ImdgListener(_parent_process, self._pubsub)

    def send_message_imdg_queue(self, _message: str) -> None:
        self._imdg.publish(self._channel_name, _message)

    def send_message_req_imdg_queue(self, protocol_id, receiver: str, *args) -> None:
        from protocol.protocol_meta import ProtocolMeta
        from protocol.protocol_owner import ProtocolOwner
        from protocol.protocol_wrapper import ProtocolWrapper

        sender = ProtocolOwner.build(
            self._parent_process.get_app_name(), self._parent_process.name
        )
        factory = ProtocolMeta.get_protocol_factory(protocol_id)
        packet = factory(sender, receiver, *args)
        envelope = ProtocolWrapper.get_protocol_wrapper(packet).get_protocol_packet_message()
        self.send_message_imdg_queue(envelope)

    def send_message_rep_imdg_queue(
        self,
        protocol_id,
        receiver: str,
        *args,
        response: ResponseInfo,
    ) -> None:
        from protocol.protocol_meta import ProtocolMeta
        from protocol.protocol_owner import ProtocolOwner
        from protocol.protocol_wrapper import ProtocolWrapper

        sender = ProtocolOwner.build(
            self._parent_process.get_app_name(), self._parent_process.name
        )
        factory = ProtocolMeta.get_protocol_factory(protocol_id)
        packet = factory(sender, receiver, *args, response=response)
        envelope = ProtocolWrapper.get_protocol_wrapper(packet).get_protocol_packet_message()
        self.send_message_imdg_queue(envelope)
