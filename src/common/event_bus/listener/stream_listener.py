import socket

import redis
from redis.client import Redis

from python_library.process.process import abProcess

from common.event_bus.listener.listener import abListener
from config.project_config import ProjectConfig
from protocol.protocol_meta import ProtocolMeta
from protocol.protocol_wrapper import ProtocolWrapper


class StreamListener(abListener):
    def __init__(self, parent_process: abProcess) -> None:
        super().__init__(parent_process)
        config = ProjectConfig.instance()
        self._redis: Redis = redis.StrictRedis(
            host=config.server_ip,
            port=int(config.server_port),
        )
        self._stream_name: str = config.stream_name
        self._group_name: str = config.stream_group_name
        self._consumer_name: str = f"{socket.gethostname()}_{parent_process.process_name}"
        self._ensure_group()

    def _ensure_group(self) -> None:
        try:
            self._redis.xgroup_create(
                self._stream_name, self._group_name, id="$", mkstream=True
            )
        except redis.exceptions.ResponseError:
            pass  # 이미 존재

    def action(self) -> None:
        messages = self._redis.xreadgroup(
            groupname=self._group_name,
            consumername=self._consumer_name,
            streams={self._stream_name: ">"},
            count=10,
            block=1000,
        )
        for _, entries in (messages or []):
            for msg_id, fields in entries:
                envelope = fields[b"data"].decode("utf-8")
                splits = ProtocolWrapper.get_split_protocol_message(envelope)
                receiver = ProtocolWrapper.get_receiver_with_splits(splits)

                wrapper, packet = ProtocolWrapper.decode_protocol_wrapper_with_message_protocol(envelope)
                ProtocolMeta.instance().get_receive_handler(wrapper.protocol_id, receiver)(
                    self._parent_process, wrapper, packet
                )
                self._redis.xack(self._stream_name, self._group_name, msg_id)
