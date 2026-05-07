from __future__ import annotations

import redis
from redis.client import Redis, PubSub

from python_library.logger.app_logger import AppLogger

from common.event_bus.event_bus import abEventBus
from common.event_bus.listener.imdg_listener import ImdgListener
from common.process.imdg_bus_process import ImdgBusProcess
from config.project_config import ProjectConfig
from protocol.message.message import IMessage, ResponseInfo
from protocol.protocol_wrapper import ProtocolWrapper


class ImdgBus(abEventBus[ImdgBusProcess]):
    def __init__(self, _parent_process: ImdgBusProcess, _channel_name: str) -> None:
        super().__init__(_parent_process)
        self._channel_name = _channel_name

        config = ProjectConfig.instance()
        self._imdg: Redis = redis.StrictRedis(host=config.server_ip, port=int(config.server_port))

        self._pubsub: PubSub = self._imdg.pubsub()
        self._pubsub.subscribe(self._channel_name)
        self.listener = ImdgListener(self._parent_process, self._pubsub)

    def send_message_imdg_queue(self, _message: str) -> None:
        self._imdg.publish(self._channel_name, _message)

    def _wrap_and_send(self, packet: IMessage) -> None:
        wrapper = ProtocolWrapper.get_protocol_wrapper(packet)
        envelope = wrapper.get_protocol_packet_message()
        log = AppLogger.instance()
        log.info(f"[IMDG SEND] channel={self._channel_name} {wrapper.summary(packet)}")
        log.debug(f"[IMDG SEND payload] {envelope}")
        self.send_message_imdg_queue(envelope)

    def send_message_req_imdg_queue(self, protocol_id, receiver: str, *args) -> None:
        from protocol.protocol_meta import ProtocolMeta
        from protocol.protocol_owner import ProtocolOwner

        sender = ProtocolOwner.build(
            self._parent_process.get_app_name(), self._parent_process.name
        )
        factory = ProtocolMeta.get_protocol_factory(protocol_id)
        packet = factory(sender, receiver, *args)
        self._wrap_and_send(packet)

    def send_message_rep_imdg_queue(
        self,
        protocol_id,
        receiver: str,
        *args,
        response: ResponseInfo,
    ) -> None:
        from protocol.protocol_meta import ProtocolMeta
        from protocol.protocol_owner import ProtocolOwner

        sender = ProtocolOwner.build(
            self._parent_process.get_app_name(), self._parent_process.name
        )
        factory = ProtocolMeta.get_protocol_factory(protocol_id)
        packet = factory(sender, receiver, *args, response=response)
        self._wrap_and_send(packet)
