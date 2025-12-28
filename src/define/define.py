from enum import IntEnum, nonmember
from typing import Self


class E_META_COLUMN(IntEnum):
    NAME = 0
    SYMBOL = 1


class E_COMMUNICATION_TYPE(IntEnum):
    IMDG = 0
    PROCESS = 1
    NORMAL = 2

    # Enum 멤버로 안 들어가게만 nonmember 유지 (타입 문자열 힌트 없음)
    META = nonmember({
        IMDG: {E_META_COLUMN.NAME: "IMDG", E_META_COLUMN.SYMBOL: "DG"},
        PROCESS: {E_META_COLUMN.NAME: "PROCESS", E_META_COLUMN.SYMBOL: "IN"},
        NORMAL: {E_META_COLUMN.NAME: "NORMAL", E_META_COLUMN.SYMBOL: "NO"},
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
