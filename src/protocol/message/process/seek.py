from dataclasses import dataclass

from protocol.message.process.process import abProcessRequestMessage, abProcessResponseMessage


@dataclass
class InrSeekReq(abProcessRequestMessage):
    start_time: str = ""


@dataclass
class InrSeekRep(abProcessResponseMessage):
    pass
