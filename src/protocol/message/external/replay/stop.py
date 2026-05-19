from dataclasses import dataclass

from protocol.message.external.external import abExternalMessage, abExternalResponseMessage


@dataclass
class PDStopReq(abExternalMessage):
    pass


@dataclass
class PDStopRep(abExternalResponseMessage):
    pass
