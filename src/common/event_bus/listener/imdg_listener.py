import time

from process.process import abProcess
from redis.client import PubSub

from src.common.event_bus.listener.listener import abListener
from src.protocol.protocol_meta import ProtocolMeta
from src.protocol.protocol_wrapper import ProtocolWrapper


class ImdgListener(abListener):
    def __init__(self, parent_process: abProcess, pubsub: PubSub):
        super().__init__(parent_process)
        self._pubsub = pubsub
        pass

    def action(self) -> None:
        for message in self._pubsub.listen():
            if message['type'] == 'message':
                message_data = message["data"].decode("utf-8")
                # test = ProtocolWrapper.decode_protocol_wrapper(message_data)

                # ProtocolMeta.get_receive_handler(test[1], test[5])(self._parent_process, message_data, message_data)
                pass

        time.sleep(1)
        pass

