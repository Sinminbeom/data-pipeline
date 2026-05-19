from dataclasses import dataclass

from define.define import E_COMMUNICATION_TYPE
from protocol.message.message import (
    E_PROTOCOL_MESSAGE_DIRECTION,
    abMessage,
)


@dataclass
class abExternalMessage(abMessage):
    """외부(UI/WebSocket) 통신 base. communication_type=EXTERNAL.
    abstract base — 직접 instantiate 안 되며 protocol_id/sender/receiver는 호출처가 명시한다.
    message_direction은 자식(abExternalResponseMessage)이 RESPONSE로 override.
    """
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.REQUEST
    communication_type: E_COMMUNICATION_TYPE = E_COMMUNICATION_TYPE.EXTERNAL


@dataclass(kw_only=True)
class abExternalResponseMessage(abExternalMessage):
    """RESPONSE PD packet. code/code_nm/reason 직접 보유.
    호출처가 코드 명시. message_direction default(=RESPONSE)는 부모 default override 역할로 유지.
    dataclass 룰상 default 뒤 no-default 필드 혼재되어 kw_only=True 필수.
    """
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE
    code: str
    code_nm: str
    reason: str
