from dataclasses import dataclass

from protocol.message.external.external import pdPacket, pdResponsePacket


@dataclass
class PDStopReq(pdPacket):
    pass


@dataclass
class PDStopRep(pdResponsePacket):
    pass
