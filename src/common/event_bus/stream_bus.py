import redis
from redis.client import Redis

from python_library.process.process import abProcess

from common.event_bus.event_bus import EventBus
from config.project_config import ProjectConfig


class StreamBus(EventBus):
    def __init__(self, parent_process: abProcess) -> None:
        super().__init__(parent_process)
        config = ProjectConfig.instance()
        self._redis: Redis = redis.StrictRedis(
            host=config.server_ip,
            port=int(config.server_port),
        )
        self._stream_name: str = config.stream_name

    def start(self) -> None:
        pass  # 발행 전용, listener 없음

    def publish(self, message: str) -> None:
        self._redis.xadd(self._stream_name, {"data": message})
