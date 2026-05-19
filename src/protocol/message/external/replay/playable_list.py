from dataclasses import dataclass, field

from protocol.message.external.external import abExternalMessage, abExternalResponseMessage
from protocol.message.external.replay.section_element import PDSectionElement


@dataclass
class PDPlayableListReq(abExternalMessage):
    vehicle_id: str = ""
    sensor_id_list: list[str] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""


@dataclass
class PDPlayableListRep(abExternalResponseMessage):
    sensor_id_list: list[str] = field(default_factory=list)
    section_list: list[PDSectionElement] = field(default_factory=list)
    # to_json/from_json override 불필요 — abExternalMessage base가 list[Dataclass] 자동 복원
