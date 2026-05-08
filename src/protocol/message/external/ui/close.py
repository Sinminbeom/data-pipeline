from dataclasses import dataclass

from protocol.message.external.external import pdPacket, pdResponsePacket


@dataclass
class PDCloseReq(pdPacket):
    pass


@dataclass
class PDCloseRep(pdResponsePacket):
    pass
