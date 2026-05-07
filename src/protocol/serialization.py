"""dataclass 메시지의 generic JSON 직렬화/역직렬화."""
from __future__ import annotations

import json
import typing
from dataclasses import asdict, is_dataclass
from typing import Any, Type, TypeVar

T = TypeVar("T")


class DataclassSerializer:
    """dataclass 메시지의 generic JSON 직렬화/역직렬화 유틸.

    `asdict`로 to_json은 평탄하지만, from_json 시 nested dataclass 필드를 자동 복원하지 않음
    (예: `list[SectionElement]`이 JSON roundtrip 후 `list[dict]`로 남음). 이 유틸이
    `typing.get_type_hints` 인트로스펙션으로 nested 필드를 재귀 복원한다.

    지원 필드 타입:
      - `list[Dataclass]`           → 각 dict를 Dataclass로 복원
      - `Optional[Dataclass]` (= `X | None`) → dict면 Dataclass로 복원
      - `Dataclass` (직접)          → dict면 Dataclass로 복원
      - primitive (str/int/list[str] 등) → 그대로 통과
    """

    @staticmethod
    def to_json(obj: Any) -> str:
        """dataclass 인스턴스를 JSON 문자열로. asdict가 nested dataclass도 재귀 dict화."""
        return json.dumps(asdict(obj))

    @staticmethod
    def from_json(target_cls: Type[T], json_string: str) -> T:
        """JSON 문자열을 dataclass 인스턴스로. nested dataclass 필드 자동 복원."""
        return DataclassSerializer._reconstruct_dataclass(target_cls, json.loads(json_string))

    @staticmethod
    def _reconstruct_dataclass(target_cls: Any, d: dict) -> Any:
        hints = typing.get_type_hints(target_cls)
        for field_name, field_type in hints.items():
            if field_name not in d or d[field_name] is None:
                continue
            d[field_name] = DataclassSerializer._reconstruct_value(field_type, d[field_name])
        return target_cls(**d)

    @staticmethod
    def _reconstruct_value(field_type: Any, value: Any) -> Any:
        origin = typing.get_origin(field_type)
        args = typing.get_args(field_type)

        # Optional[X] / X | None → 비-None 타입으로 unwrap 후 재귀
        if origin is typing.Union or DataclassSerializer._is_union_type(origin):
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                return DataclassSerializer._reconstruct_value(non_none_args[0], value)
            return value  # 복합 Union은 손대지 않음

        # list[X] → X가 dataclass면 각 요소 복원
        if origin is list and args:
            item_type = args[0]
            if is_dataclass(item_type) and isinstance(value, list):
                return [
                    DataclassSerializer._reconstruct_dataclass(item_type, item)
                    if isinstance(item, dict) else item
                    for item in value
                ]
            return value

        # 직접 dataclass 필드 (예: ResponseInfo)
        if is_dataclass(field_type) and isinstance(value, dict):
            return DataclassSerializer._reconstruct_dataclass(field_type, value)

        return value

    @staticmethod
    def _is_union_type(origin: Any) -> bool:
        """Python 3.10+ `X | Y` syntax는 typing.Union이 아닌 types.UnionType. 둘 다 처리."""
        import types
        return origin is types.UnionType  # noqa: E721
