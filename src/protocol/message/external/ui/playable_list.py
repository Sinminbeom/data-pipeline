from dataclasses import dataclass

from src.define.define import E_COMMUNICATION_TYPE
from src.protocol.message.external.external import ExternalPacket
from src.protocol.message.external.ui.section_element import PDSectionElement
from src.protocol.message.packet import Header, E_PROTOCOL_MESSAGE_DIRECTION


@dataclass
class PDPlayableListRep(ExternalPacket):
    sensor_id_list: list[str]
    section_list : list[PDSectionElement]

    def __init__(
        self,
        protocol_id: str,
        sender: str,
        receiver: str,
        sensor_id_list: list,
        section_list: list[PDSectionElement]
    ) -> None:
        super().__init__(
            header=Header(
                communication_type=E_COMMUNICATION_TYPE.NORMAL,
                protocol_id=protocol_id,
                sender=sender,
                receiver=receiver,
            )
        )
        self.sensor_id_list = sensor_id_list
        self.section_list = section_list


@dataclass
class PDPlayableListReq(ExternalPacket):
    vehicle_id: str
    sensor_id_list: list[str]
    start_time: str
    end_time: str

    def __init__(
        self,
        protocol_id: str,
        message_direction: int,
        sender: str,
        receiver: str,
        vehicle_id: str,
        sensor_id_list: list,
        start_time: str,
        end_time: str
    ) -> None:
        super().__init__(
            header=Header(
                communication_type=E_COMMUNICATION_TYPE.NORMAL,
                message_direction=E_PROTOCOL_MESSAGE_DIRECTION(message_direction),
                protocol_id=protocol_id,
                sender=sender,
                receiver=receiver,
            )
        )
        self.vehicle_id = vehicle_id
        self.sensor_id_list = sensor_id_list
        self.start_time = start_time
        self.end_time = end_time