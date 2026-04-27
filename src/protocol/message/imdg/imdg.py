from dataclasses import dataclass

from define.define import E_COMMUNICATION_TYPE
from protocol.message.message import (
    abProtocolMessage,
    E_PROTOCOL_MESSAGE_DIRECTION,
)


@dataclass
class abImdgMessage(abProtocolMessage):
    """앱 간 통신. communication_type=IMDG."""
    communication_type: E_COMMUNICATION_TYPE = E_COMMUNICATION_TYPE.IMDG


@dataclass
class abImdgRequestMessage(abImdgMessage):
    """IMDG REQUEST. message_direction=REQUEST."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.REQUEST


@dataclass
class abImdgResponseMessage(abImdgMessage):
    """IMDG RESPONSE. message_direction=RESPONSE."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE


@dataclass
class abImdgNotiMessage(abImdgMessage):
    """IMDG NOTI. message_direction=NOTI."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.NOTI
