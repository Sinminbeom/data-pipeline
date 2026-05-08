from dataclasses import dataclass

from protocol.message.process.process import abProcessRequestMessage, abProcessResponseMessage


@dataclass
class InrCloseReq(abProcessRequestMessage):
    pass


@dataclass
class InrCloseRep(abProcessResponseMessage):
    pass
