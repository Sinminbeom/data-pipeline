from dataclasses import dataclass

from protocol.message.external.external import abExternalMessage, abExternalResponseMessage


@dataclass
class PDSeekReq(abExternalMessage):
    start_time: str = ""


@dataclass
class PDSeekRep(abExternalResponseMessage):
    pass
