from dataclasses import dataclass

from protocol.message.process.process import abProcessRequestMessage, abProcessResponseMessage


@dataclass
class InrPauseReq(abProcessRequestMessage):
    pass


@dataclass
class InrPauseRep(abProcessResponseMessage):
    pass
