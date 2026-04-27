from __future__ import annotations

from dataclasses import dataclass

from protocol.message.ipc.ipc import ImdgRequestPacket


@dataclass
class PlayableListReq(ImdgRequestPacket):

    vehicle_id: str = ""
    sensor_id_list: list = None
    start_time: str = ""
    end_time: str = ""

    def __init__(
        self,
        protocol_id: str,
        sender: str,
        receiver: str,
        vehicle_id: str,
        sensor_id_list: list,
        start_time: str,
        end_time: str,
    ) -> None:
        super().__init__(protocol_id=protocol_id, sender=sender, receiver=receiver)
        self.vehicle_id = vehicle_id
        self.sensor_id_list = sensor_id_list
        self.start_time = start_time
        self.end_time = end_time
