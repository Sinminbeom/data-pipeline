import json
from dataclasses import asdict, dataclass, field

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

    def to_json(self) -> str:
        d = asdict(self)
        d["section_list"] = [asdict(s) for s in self.section_list]
        return json.dumps(d)

    @classmethod
    def from_json(cls, json_string: str) -> "PDPlayableListRep":
        d = json.loads(json_string)
        if d.get("section_list") is not None:
            d["section_list"] = [PDSectionElement(**s) for s in d["section_list"]]
        return cls(**d)
