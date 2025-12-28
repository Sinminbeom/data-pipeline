from __future__ import annotations

from dataclasses import dataclass

from src.define.define import E_COMMUNICATION_TYPE
from src.protocol.message.ipc.ipc import IpcRequestPacket
from src.protocol.message.packet import Header, E_PROTOCOL_MESSAGE_DIRECTION


@dataclass
class PlayableListReq(IpcRequestPacket):

    vehicle_id: str = ""
    sensor_id_list: list = None
    start_time: str = ""
    end_time: str = ""

    def __init__(
        self,
        protocol_id: str,
        message_direction: int,
        sender: str,
        receiver: str,
        vehicle_id: str,
        sensor_id_list: list,
        start_time: str,
        end_time: str,
    ) -> None:
        super().__init__(
            header=Header(
                communication_type=E_COMMUNICATION_TYPE.IMDG,
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
