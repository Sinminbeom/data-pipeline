from enum import IntEnum, nonmember
from typing import Self


class E_META_COLUMN(IntEnum):
    NAME = 0
    SYMBOL = 1


class E_COMMUNICATION_TYPE(IntEnum):
    """통신 채널 분류. 3차원:
    - IMDG: inter-app (시스템 내 다른 서비스/서버 간, Redis pub/sub)
    - PROCESS: intra-app (같은 앱 내 자식 프로세스 IPC)
    - EXTERNAL: external/public (UI/WebSocket 클라이언트와의 외부 API)
    """
    IMDG = 0
    PROCESS = 1
    EXTERNAL = 2

    # Enum 멤버로 안 들어가게만 nonmember 유지 (타입 문자열 힌트 없음)
    META = nonmember({
        IMDG: {E_META_COLUMN.NAME: "IMDG", E_META_COLUMN.SYMBOL: "IMDG"},
        PROCESS: {E_META_COLUMN.NAME: "PROCESS", E_META_COLUMN.SYMBOL: "PROCESS"},
        EXTERNAL: {E_META_COLUMN.NAME: "EXTERNAL", E_META_COLUMN.SYMBOL: "EXTERNAL"},
    })

    _SYMBOL_TO_TYPE = nonmember(None)  # dict[str, E_COMMUNICATION_TYPE] | None

    @classmethod
    def _build_symbol_map(cls) -> dict[str, Self]:
        return {
            meta[E_META_COLUMN.SYMBOL]: comm_type
            for comm_type, meta in cls.META.items()
        }

    @classmethod
    def get_symbol(cls, communication_type: Self) -> str:
        return cls.META[communication_type][E_META_COLUMN.SYMBOL]

    @classmethod
    def get_name(cls, communication_type: Self) -> str:
        return cls.META[communication_type][E_META_COLUMN.NAME]

    @classmethod
    def symbol_to_type(cls, symbol: str) -> Self | None:
        if cls._SYMBOL_TO_TYPE is None:
            cls._SYMBOL_TO_TYPE = cls._build_symbol_map()
        return cls._SYMBOL_TO_TYPE.get(symbol)
