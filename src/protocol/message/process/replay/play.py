from dataclasses import dataclass

from protocol.message.process.process import abProcessRequestMessage, abProcessResponseMessage


@dataclass
class InrPlayReq(abProcessRequestMessage):
    section_id: int = 0
    vehicle_id: str = ""
    start_time: str = ""
    end_time: str = ""


@dataclass
class InrPlayRep(abProcessResponseMessage):
    pass
