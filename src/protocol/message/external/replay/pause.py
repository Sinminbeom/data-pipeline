from dataclasses import dataclass

from protocol.message.external.external import abExternalMessage, abExternalResponseMessage


@dataclass
class PDPauseReq(abExternalMessage):
    pass


@dataclass
class PDPauseRep(abExternalResponseMessage):
    pass
