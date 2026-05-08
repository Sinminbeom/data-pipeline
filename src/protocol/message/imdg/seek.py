from dataclasses import dataclass

from protocol.message.imdg.imdg import abImdgRequestMessage, abImdgResponseMessage


@dataclass
class SeekReq(abImdgRequestMessage):
    start_time: str = ""


@dataclass
class SeekRep(abImdgResponseMessage):
    pass
