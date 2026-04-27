from dataclasses import dataclass

from define.define import E_COMMUNICATION_TYPE
from protocol.message.message import (
    abProtocolMessage,
    E_PROTOCOL_MESSAGE_DIRECTION,
)


@dataclass
class abProcessMessage(abProtocolMessage):
    """앱 내 자식 프로세스 간 통신. communication_type=PROCESS."""
    communication_type: E_COMMUNICATION_TYPE = E_COMMUNICATION_TYPE.PROCESS


@dataclass
class abProcessRequestMessage(abProcessMessage):
    """PROCESS REQUEST. message_direction=REQUEST."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.REQUEST


@dataclass
class abProcessResponseMessage(abProcessMessage):
    """PROCESS RESPONSE. message_direction=RESPONSE."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE


@dataclass
class abProcessNotiMessage(abProcessMessage):
    """PROCESS NOTI. message_direction=NOTI."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.NOTI
