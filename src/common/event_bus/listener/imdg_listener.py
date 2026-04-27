import time

from python_library.process.process import abProcess
from redis.client import PubSub

from common.event_bus.listener.listener import abListener
from define.define import E_COMMUNICATION_TYPE
from protocol.protocol_meta import ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class ImdgListener(abListener):
    def __init__(self, parent_process: abProcess, pubsub: PubSub):
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
                ProtocolMeta.get_receive_handler(wrapper.protocol_id, receiver)(
                    self._parent_process, wrapper, packet
                )

        time.sleep(0.001)
        pass
