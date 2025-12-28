from dataclasses import dataclass

from src.define.define import E_COMMUNICATION_TYPE
from src.protocol.message.ipc.ipc import IpcRequestPacket, IpcResponsePacket
from src.protocol.message.packet import Header


# -----------------------------
# INR Playable List - Request
# -----------------------------

@dataclass
class InrPlayableListReq(IpcRequestPacket):
    vehicle_id: str = ""
    start_time: str = ""
    end_time: str = ""

    def __init__(
        self,
        protocol_id: str,
        sender: str,
        receiver: str,
        vehicle_id: str,
        start_time: str,
        end_time: str,
    ) -> None:
        super().__init__(
            header=Header(
                communication_type=E_COMMUNICATION_TYPE.PROCESS,
                protocol_id=protocol_id,
                sender=sender,
                receiver=receiver,
            )
        )
        self.vehicle_id = vehicle_id
        self.start_time = start_time
        self.end_time = end_time


# -----------------------------
# INR Playable List - Response
# -----------------------------

@dataclass
class InrPlayableListRep(IpcResponsePacket):
    sensor_id: str = ""
    section_list: list = None
    return_message: str = ""

    def __init__(
        self,
        protocol_id: str,
        sender: str,
        receiver: str,
        sensor_id: str,
        section_list: list,
        return_message: str,
    ) -> None:
        super().__init__(
            header=Header(
                communication_type=E_COMMUNICATION_TYPE.PROCESS,
                protocol_id=protocol_id,
                sender=sender,
                receiver=receiver,
            ),
            return_code=None
        )

        self.sensor_id = sensor_id
        self.section_list = section_list
        self.return_message = return_message
