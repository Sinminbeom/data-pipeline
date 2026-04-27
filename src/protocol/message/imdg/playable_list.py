from dataclasses import dataclass, field

from protocol.message.imdg.imdg import abImdgRequestMessage, abImdgResponseMessage


@dataclass
class PlayableListReq(abImdgRequestMessage):
    vehicle_id: str = ""
    sensor_id_list: list[str] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""


@dataclass
class PlayableListRep(abImdgResponseMessage):
    sensor_id_list: list[str] = field(default_factory=list)
    section_list: list = field(default_factory=list)
