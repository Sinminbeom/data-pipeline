from dataclasses import dataclass
from typing import Type

from src.protocol.message.packet import Packet, T


@dataclass
class ExternalPacket(Packet):

    def to_json(self) -> str:
        # 내부 저장/디버깅/로그 목적
        return self._encode_internal(self)

    def to_json_public(self) -> str:
        # 외부 전송 목적
        return self._encode_external(self)

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        # 외부에서 수신한 raw를 객체로 복원(프로젝트의 internal decoder를 사용)
        return cls._decode_internal(expected_type=cls, json_data=json_data)

