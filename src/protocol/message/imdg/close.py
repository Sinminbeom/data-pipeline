from dataclasses import dataclass

from protocol.message.imdg.imdg import abImdgRequestMessage, abImdgResponseMessage


@dataclass
class CloseReq(abImdgRequestMessage):
    pass


@dataclass
class CloseRep(abImdgResponseMessage):
    pass
