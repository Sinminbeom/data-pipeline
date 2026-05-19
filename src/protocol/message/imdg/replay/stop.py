from dataclasses import dataclass

from protocol.message.imdg.imdg import abImdgRequestMessage, abImdgResponseMessage


@dataclass
class StopReq(abImdgRequestMessage):
    pass


@dataclass
class StopRep(abImdgResponseMessage):
    pass
