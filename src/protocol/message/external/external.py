import json
from dataclasses import asdict, dataclass

from protocol.message.message import IMessage, E_PROTOCOL_MESSAGE_DIRECTION


@dataclass
class pdPacket(IMessage):
    """외부(UI/WebSocket) 통신 base. communication_type 없음, plain flat dataclass."""
    protocol_id: str = ""
    sender: str = ""
    receiver: str = ""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.REQUEST

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_string: str):
        return cls(**json.loads(json_string))


@dataclass
class pdResponsePacket(pdPacket):
    """RESPONSE PD packet. code/code_nm/reason 직접 보유 (replayer 동일)."""
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION = E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE
    code: str = ""
    code_nm: str = ""
    reason: str = ""
