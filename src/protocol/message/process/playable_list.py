from dataclasses import dataclass, field

from protocol.message.process.process import abProcessRequestMessage, abProcessResponseMessage


@dataclass
class InrPlayableListReq(abProcessRequestMessage):
    vehicle_id: str = ""
    start_time: str = ""
    end_time: str = ""


@dataclass
class InrPlayableListRep(abProcessResponseMessage):
    sensor_id: str = ""
    section_list: list = field(default_factory=list)
