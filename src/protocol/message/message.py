from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import IntEnum
from typing import Self

from define.define import E_COMMUNICATION_TYPE
from protocol.serialization import DataclassSerializer


class IMessage(ABC):
    """직렬화 contract. 모든 message/packet은 to_json/from_json을 가진다."""

    @abstractmethod
    def to_json(self) -> str: ...

    @classmethod
    @abstractmethod
    def from_json(cls, json_string: str) -> Self: ...


class E_PROTOCOL_MESSAGE_DIRECTION(IntEnum):
    REQUEST = 0
    RESPONSE = 1
    NOTI = 2


@dataclass
class ResponseInfo:
    """RESPONSE message가 가지는 응답 코드 정보. composition 용."""
    code: str = ""
    code_nm: str = ""
    reason: str = ""


@dataclass
class abMessage(IMessage):
    """내부 통신(IMDG/PROCESS) base. 라우팅 필드 + direction을 root level 평탄화.
    abstract base — 직접 instantiate 안 되며 모든 필수 필드는 호출처가 명시한다.
    communication_type / message_direction은 자식 계층(abImdgMessage, abProcessMessage 등)이 고정.

    필드 순서 주의: message_direction이 communication_type보다 앞. 자식 계층에서
    communication_type을 먼저 default 부여(abImdgMessage 등)하므로 default 있는 필드를 뒤로 정렬.
    """
    protocol_id: str
    sender: str
    receiver: str
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION
    communication_type: E_COMMUNICATION_TYPE

    def to_json(self) -> str:
        return DataclassSerializer.to_json(self)

    @classmethod
    def from_json(cls, json_string: str) -> Self:
        return DataclassSerializer.from_json(cls, json_string)
