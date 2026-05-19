from dataclasses import dataclass

from protocol.message.external.external import abExternalMessage, abExternalResponseMessage


@dataclass
class PDCloseReq(abExternalMessage):
    pass


@dataclass
class PDCloseRep(abExternalResponseMessage):
    pass
