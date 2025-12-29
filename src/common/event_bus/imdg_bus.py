import redis
from redis.client import Redis, PubSub
from abc import abstractmethod

from process.process import abProcess

from src.common.event_bus.event_bus import EventBus
from src.common.event_bus.listener.imdg_listener import ImdgListener


class ImdgBus(EventBus):
    def __init__(self, _parent_process: abProcess, _channel_name: str) -> None:
        super().__init__(_parent_process)
        self._channel_name = _channel_name

        # TODO: redis 설정파일
        self._imdg: Redis = redis.StrictRedis(host="localhost", port=6379)

        self._pubsub: PubSub = self._imdg.pubsub()
        self._pubsub.subscribe(self._channel_name)
        self.listener = ImdgListener(_parent_process, self._pubsub)

    @abstractmethod
    def send_message_imdg_queue(self, _message: str) -> None:
        self._imdg.publish(self._channel_name, _message)