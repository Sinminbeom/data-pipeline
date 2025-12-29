from enum import IntEnum

from src.define.define import E_COMMUNICATION_TYPE
from src.protocol.message.packet import Packet
from src.utils.jsonpickle_util import JsonpickleUtil
from src.utils.string_builder import StringBuilder
from src.utils.time_string_fit import TimeStringFit, E_TIMEFORMAT

# TODO: 정리할것
class ProtocolWrapper:
    DELIM_CHAR = "|:|"

    class E_PROTOCOL_MESSAGE_ELE(IntEnum):
        COMMUNICATION_TYPE = 0
        MESSAGE_ID = 1
        PROTOCOL_ID = 2
        MESSAGE_DIRECTION = 3
        SENDER = 4
        RECEIVER = 5
        PROTOCOL_MESSAGE = 6

    sequence_id = dict()

    def __init__(self, message_id, protocol_message: Packet):
        try:
            self.communication_type = protocol_message.header.communication_type
        except Exception as e:
            self.communication_type = E_COMMUNICATION_TYPE.NORMAL

        self.protocol_id = protocol_message.header.protocol_id
        self.message_direction = protocol_message.header.message_direction
        self.sender = protocol_message.header.sender
        self.receiver = protocol_message.header.receiver
        self.protocol_message = protocol_message
        self.message_id = message_id

    def get_protocol_packet_message(self) -> str:
        sb = StringBuilder()
        sb.append(E_COMMUNICATION_TYPE.get_symbol(self.communication_type)).append(self.DELIM_CHAR) \
            .append(self.message_id).append(self.DELIM_CHAR) \
            .append(self.protocol_id).append(self.DELIM_CHAR) \
            .append(self.message_direction).append(self.DELIM_CHAR) \
            .append(self.sender).append(self.DELIM_CHAR) \
            .append(self.receiver).append(self.DELIM_CHAR) \
            .append(JsonpickleUtil.encode_internal(self.protocol_message))
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
    def get_protocol_wrapper(protocol_message_object):
        message_id = ProtocolWrapper.get_sequence_id_now()
        return ProtocolWrapper(message_id, protocol_message_object)

    @staticmethod
    def decode_protocol_wrapper(protocol_message_string):
        s = protocol_message_string.split(ProtocolWrapper.DELIM_CHAR)

        communication_type = s[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.COMMUNICATION_TYPE]
        message_id = s[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.MESSAGE_ID]
        protocol_id = s[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.PROTOCOL_ID]
        message_direction = s[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.MESSAGE_DIRECTION]
        sender = s[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.SENDER]
        receiver = s[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.RECEIVER]
        protocol_message = s[ProtocolWrapper.E_PROTOCOL_MESSAGE_ELE.PROTOCOL_MESSAGE]

        return communication_type, protocol_id, message_id, message_direction, sender, receiver, protocol_message
