from dataclasses import dataclass

from protocol.message.imdg.imdg import abImdgRequestMessage, abImdgResponseMessage


@dataclass
class PauseReq(abImdgRequestMessage):
    pass


@dataclass
class PauseRep(abImdgResponseMessage):
    pass
