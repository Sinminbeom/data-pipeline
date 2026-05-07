from dataclasses import dataclass
from enum import IntEnum

from define.define import E_COMMUNICATION_TYPE
from protocol.serialization import DataclassSerializer


class IMessage:
    """모든 message/packet 공통 base. 라우팅 필드 + to_json 인터페이스 정의."""
    protocol_id: str
    sender: str
    receiver: str
    message_direction: "E_PROTOCOL_MESSAGE_DIRECTION"

    def to_json(self) -> str:
        raise NotImplementedError


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
class abProtocolMessage(IMessage):
    """내부 통신(IMDG/PROCESS) base. 라우팅 필드 + direction을 root level 평탄화."""
    protocol_id: str = ""
    sender: str = ""
    receiver: str = ""
    communication_type: E_COMMUNICATION_TYPE = E_COMMUNICATION_TYPE.IMDG
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.REQUEST
    response: ResponseInfo | None = None

    def to_json(self) -> str:
        return DataclassSerializer.to_json(self)

    @classmethod
    def from_json(cls, json_string: str):
        return DataclassSerializer.from_json(cls, json_string)
