from dataclasses import dataclass

from protocol.message.external.external import pdPacket, pdResponsePacket


@dataclass
class PDSeekReq(pdPacket):
    start_time: str = ""


@dataclass
class PDSeekRep(pdResponsePacket):
    pass
