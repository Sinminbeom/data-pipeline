from dataclasses import dataclass, field

from protocol.message.external.external import pdPacket, pdResponsePacket
from protocol.message.external.ui.section_element import PDSectionElement


@dataclass
class PDPlayableListReq(pdPacket):
    vehicle_id: str = ""
    sensor_id_list: list[str] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""


@dataclass
class PDPlayableListRep(pdResponsePacket):
    sensor_id_list: list[str] = field(default_factory=list)
    section_list: list[PDSectionElement] = field(default_factory=list)
    # to_json/from_json override 불필요 — pdPacket base가 list[Dataclass] 자동 복원
