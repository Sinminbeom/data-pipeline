from dataclasses import dataclass

from protocol.message.process.process import abProcessRequestMessage, abProcessResponseMessage


@dataclass
class InrStopReq(abProcessRequestMessage):
    pass


@dataclass
class InrStopRep(abProcessResponseMessage):
    pass
