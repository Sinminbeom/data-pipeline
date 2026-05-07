from __future__ import annotations

import time

from python_library.logger.app_logger import AppLogger
from redis.client import PubSub

from common.event_bus.listener.listener import abListener
from common.process.imdg_bus_process import ImdgBusProcess
from define.define import E_COMMUNICATION_TYPE
from protocol.protocol_meta import ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class ImdgListener(abListener[ImdgBusProcess]):
    def __init__(self, parent_process: ImdgBusProcess, pubsub: PubSub):
        super().__init__(parent_process)
        self._pubsub = pubsub

    def action(self) -> None:
        for message in self._pubsub.listen():
            if message['type'] == 'message':
                envelope = message["data"].decode("utf-8")
                splits = ProtocolWrapper.get_split_protocol_message(envelope)
                receiver = ProtocolWrapper.get_receiver_with_splits(splits)

                if self._parent_process.is_ignore(E_COMMUNICATION_TYPE.IMDG, receiver):
                    continue

                wrapper, packet = ProtocolWrapper.decode_protocol_wrapper_with_message_protocol(envelope)

                log = AppLogger.instance()
                log.info(f"[IMDG RECV] {wrapper.summary(packet)}")
                log.debug(f"[IMDG RECV payload] {envelope}")

                ProtocolMeta.get_receive_handler(wrapper.protocol_id, receiver)(
                    self._parent_process, wrapper, packet
                )

        time.sleep(0.001)
        pass
