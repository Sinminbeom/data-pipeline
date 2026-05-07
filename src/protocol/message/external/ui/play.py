from dataclasses import dataclass, field

from protocol.message.external.external import pdPacket, pdResponsePacket


@dataclass
class PDPlayReq(pdPacket):
    section_id: int = 0
    vehicle_id: str = ""
    sensor_id_list: list[str] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""


@dataclass
class PDPlayRep(pdResponsePacket):
    pass
