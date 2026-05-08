from dataclasses import dataclass

from protocol.message.external.external import pdPacket, pdResponsePacket


@dataclass
class PDPauseReq(pdPacket):
    pass


@dataclass
class PDPauseRep(pdResponsePacket):
    pass
