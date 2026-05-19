from enum import IntEnum

from define.define import E_COMMUNICATION_TYPE
from protocol.message.message import E_PROTOCOL_MESSAGE_DIRECTION, IMessage, abMessage
from utils.string_builder import StringBuilder
from utils.time_string_fit import TimeStringFit, E_TIMEFORMAT


class ProtocolWrapper:
    DELIM_CHAR = "|:|"

    class E_PROTOCOL_MESSAGE_ELE(IntEnum):
        COMMUNICATION_TYPE = 0
        MESSAGE_ID = 1
        MESSAGE_DIRECTION = 2
        PROTOCOL_ID = 3
        SENDER = 4
        RECEIVER = 5
        PROTOCOL_MESSAGE = 6

    sequence_id = dict()

    def __init__(self, message_id: str, protocol_message: IMessage):
        # IMessage는 직렬화 contract만 보장 — 라우팅 필드는 abMessage 계열에만 있음.
        # wrapper는 라우팅 필드를 root level로 평탄화하므로 narrowing이 필요하다.
        assert isinstance(protocol_message, abMessage), (
            f"ProtocolWrapper는 abMessage 계열만 받는다. got={type(protocol_message).__name__}"
        )
        self.communication_type = protocol_message.communication_type
        self.protocol_id = protocol_message.protocol_id
        self.message_direction = protocol_message.message_direction
        self.sender = protocol_message.sender
        self.receiver = protocol_message.receiver
        self.protocol_message = protocol_message
        self.message_id = message_id

    def summary(self, packet: IMessage | None = None) -> str:
        direction = E_PROTOCOL_MESSAGE_DIRECTION(int(self.message_direction)).name
        base = f"proto={self.protocol_id} dir={direction} {self.sender}->{self.receiver}"
        response = getattr(packet, "response", None) if packet is not None else None
        if response is not None:
            base += f" code={response.code}"
        return base

    def get_protocol_packet_message(self) -> str:
        sb = StringBuilder()
        sb.append(E_COMMUNICATION_TYPE.get_symbol(self.communication_type)).append(self.DELIM_CHAR) \
            .append(self.message_id).append(self.DELIM_CHAR) \
            .append(self.message_direction).append(self.DELIM_CHAR) \
            .append(self.protocol_id).append(self.DELIM_CHAR) \
            .append(self.sender).append(self.DELIM_CHAR) \
            .append(self.receiver).append(self.DELIM_CHAR) \
            .append(self.protocol_message.to_json())
        return sb.to_string()

    @staticmethod
    def get_sequence_id_now() -> str:
        field_key = TimeStringFit().get(E_TIMEFORMAT.YYYYMMDDHH24MI)

        if field_key in ProtocolWrapper.sequence_id:
            ProtocolWrapper.sequence_id[field_key] += 1
        else:
            ProtocolWrapper.sequence_id[field_key] = 0

        seq = int(ProtocolWrapper.sequence_id[field_key])
        return field_key + "_" + f"{seq:08}"

    @staticmethod
    def get_protocol_wrapper(protocol_message: IMessage) -> "ProtocolWrapper":
        message_id = ProtocolWrapper.get_sequence_id_now()
        return ProtocolWrapper(message_id, protocol_message)

    @staticmethod
    def get_split_protocol_message(protocol_message_string: str) -> list[str]:
        return protocol_message_string.split(ProtocolWrapper.DELIM_CHAR)

    @staticmethod
    def get_communication_type_with_splits(splits: list[str]) -> str:
        return splits[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.COMMUNICATION_TYPE]

    @staticmethod
    def get_protocol_id_with_splits(splits: list[str]) -> str:
        return splits[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.PROTOCOL_ID]

    @staticmethod
    def get_receiver_with_splits(splits: list[str]) -> str:
        return splits[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.RECEIVER]

    @staticmethod
    def decode_protocol_wrapper(protocol_message_string: str) -> "ProtocolWrapper":
        wrapper, _ = ProtocolWrapper.decode_protocol_wrapper_with_message_protocol(protocol_message_string)
        return wrapper

    @staticmethod
    def decode_protocol_wrapper_with_message_protocol(
        protocol_message_string: str,
    ) -> tuple["ProtocolWrapper", IMessage]:
        from protocol.protocol_meta import ProtocolMeta

        splits = ProtocolWrapper.get_split_protocol_message(protocol_message_string)

        message_id = splits[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.MESSAGE_ID]
        protocol_id = splits[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.PROTOCOL_ID]
        protocol_message_json = splits[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.PROTOCOL_MESSAGE]

        message = ProtocolMeta.instance().get_json_decoder(protocol_id)(protocol_message_json)
        wrapper = ProtocolWrapper(message_id, message)
        return wrapper, message
