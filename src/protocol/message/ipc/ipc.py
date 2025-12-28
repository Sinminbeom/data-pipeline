from dataclasses import dataclass
from typing import Type

from src.protocol.message.packet import Packet, T


@dataclass(frozen=True)
class Response:
    code: int
    name: str
    reason: str


@dataclass
class IpcPacket(Packet):

    def to_json(self) -> str:
        return self._encode_internal(self)

    def to_json_public(self) -> str:
        # IPC는 보통 외부 전송용이 아니지만, 디버깅/로그 등으로 사용할 수 있도록 제공
        return self._encode_external(self)

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        return cls._decode_internal(expected_type=cls, json_data=json_data)
    pass


@dataclass
class IpcRequestPacket(IpcPacket):
    pass


@dataclass
class IpcResponsePacket(IpcPacket):
    response: Response
    pass