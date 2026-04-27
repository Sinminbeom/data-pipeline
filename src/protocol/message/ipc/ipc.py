from dataclasses import dataclass
from typing import Type

from define.define import E_COMMUNICATION_TYPE
from protocol.message.packet import (
    Header,
    E_PROTOCOL_MESSAGE_DIRECTION,
    abPacket,
    T,
)


@dataclass(frozen=True)
class Response:
    code: int
    name: str
    reason: str


@dataclass
class IpcPacket(abPacket):

    def to_json(self) -> str:
        return self._encode_internal(self)

    def to_json_public(self) -> str:
        # IPC는 보통 외부 전송용이 아니지만, 디버깅/로그 등으로 사용할 수 있도록 제공
        return self._encode_external(self)

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        return cls._decode_internal(expected_type=cls, json_data=json_data)


@dataclass
class ImdgPacket(IpcPacket):
    """앱 간 통신 packet. communication_type=IMDG 자동 부여."""

    def __init__(
        self,
        protocol_id: str,
        message_direction: E_PROTOCOL_MESSAGE_DIRECTION,
        sender: str,
        receiver: str,
    ) -> None:
        super().__init__(
            header=Header(
                communication_type=E_COMMUNICATION_TYPE.IMDG,
                message_direction=message_direction,
                protocol_id=protocol_id,
                sender=sender,
                receiver=receiver,
            )
        )


@dataclass
class ImdgRequestPacket(ImdgPacket):
    """IMDG REQUEST packet. message_direction=REQUEST 자동 부여."""

    def __init__(self, protocol_id: str, sender: str, receiver: str) -> None:
        super().__init__(
            protocol_id=protocol_id,
            message_direction=E_PROTOCOL_MESSAGE_DIRECTION.REQUEST,
            sender=sender,
            receiver=receiver,
        )


@dataclass
class ImdgResponsePacket(ImdgPacket):
    """IMDG RESPONSE packet. message_direction=RESPONSE 자동 부여."""

    response: Response

    def __init__(
        self,
        protocol_id: str,
        sender: str,
        receiver: str,
        response: Response,
    ) -> None:
        super().__init__(
            protocol_id=protocol_id,
            message_direction=E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE,
            sender=sender,
            receiver=receiver,
        )
        self.response = response


@dataclass
class InnerPacket(IpcPacket):
    """앱 내 자식 프로세스 간 통신 packet. communication_type=INNER 자동 부여."""

    def __init__(
        self,
        protocol_id: str,
        message_direction: E_PROTOCOL_MESSAGE_DIRECTION,
        sender: str,
        receiver: str,
    ) -> None:
        super().__init__(
            header=Header(
                communication_type=E_COMMUNICATION_TYPE.INNER,
                message_direction=message_direction,
                protocol_id=protocol_id,
                sender=sender,
                receiver=receiver,
            )
        )


@dataclass
class InnerRequestPacket(InnerPacket):
    """INNER REQUEST packet. message_direction=REQUEST 자동 부여."""

    def __init__(self, protocol_id: str, sender: str, receiver: str) -> None:
        super().__init__(
            protocol_id=protocol_id,
            message_direction=E_PROTOCOL_MESSAGE_DIRECTION.REQUEST,
            sender=sender,
            receiver=receiver,
        )


@dataclass
class InnerResponsePacket(InnerPacket):
    """INNER RESPONSE packet. message_direction=RESPONSE 자동 부여."""

    response: Response

    def __init__(
        self,
        protocol_id: str,
        sender: str,
        receiver: str,
        response: Response,
    ) -> None:
        super().__init__(
            protocol_id=protocol_id,
            message_direction=E_PROTOCOL_MESSAGE_DIRECTION.RESPONSE,
            sender=sender,
            receiver=receiver,
        )
        self.response = response
