import time
import json

from python_library.process.process import abProcess
from redis.client import PubSub

from common.event_bus.listener.listener import abListener
from define.define import E_COMMUNICATION_TYPE
from protocol.protocol_meta import ProtocolMeta


class ImdgListener(abListener):
    def __init__(self, parent_process: abProcess, pubsub: PubSub):
        super().__init__(parent_process)
        self._pubsub = pubsub

    def action(self) -> None:
        for message in self._pubsub.listen():
            if message['type'] == 'message':
                message_data = message["data"].decode("utf-8")
                json_data = json.loads(message_data)
                protocol_id = json_data['header']['protocol_id']
                receiver = json_data['header']['receiver']

                if self._parent_process.is_ignore(E_COMMUNICATION_TYPE.IMDG, receiver):
                    continue

                packet = ProtocolMeta.get_json_decoder(protocol_id)(message_data)
                ProtocolMeta.get_receive_handler(protocol_id, receiver)(self._parent_process, packet)

        time.sleep(0.001)
        pass

