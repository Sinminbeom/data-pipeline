from python_library.define.enum import IENUM


class IPCap:
    class E_TCP_FLAG(IENUM):
        ACK_AND_PSH = 24

    class E_PROTOCOL(IENUM):
        UDP = 17
        TCP = 6

    class E_LINK_TYPE(IENUM):
        ETHERNET = 1
        LINUX_SLL = 113
        LINUX_SLL_V2 = 276


class IDTO:
    """Pool 보관용 marker base — replayer App/Common/cDto.IDTO 미러."""
    pass
