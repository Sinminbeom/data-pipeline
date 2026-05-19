from dataclasses import dataclass

from define.define import E_COMMUNICATION_TYPE
from protocol.message.message import (
    abMessage,
    E_PROTOCOL_MESSAGE_DIRECTION,
    ResponseInfo,
)


@dataclass
class abProcessMessage(abMessage):
    """앱 내 자식 프로세스 간 통신. communication_type=PROCESS."""
    communication_type: E_COMMUNICATION_TYPE = E_COMMUNICATION_TYPE.PROCESS


@dataclass
class abProcessRequestMessage(abProcessMessage):
    """PROCESS REQUEST. message_direction=REQUEST."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.REQUEST


@dataclass
class abProcessResponseMessage(abProcessMessage):
    """PROCESS RESPONSE. message_direction=RESPONSE. response 보유."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE
    response: ResponseInfo | None = None


@dataclass
class abProcessNotiMessage(abProcessMessage):
    """PROCESS NOTI. message_direction=NOTI."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.NOTI
