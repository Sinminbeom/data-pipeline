from __future__ import annotations

from typing import Any, Optional, Type, TypeVar, cast
import jsonpickle

T = TypeVar("T")


class JsonpickleUtil:
    @staticmethod
    def encode_internal(obj: Any) -> str:
        """내부용: 타입 메타 포함(복원 가능)."""
        return jsonpickle.encode(obj, unpicklable=True, make_refs=False)

    @staticmethod
    def encode_external(obj: Any) -> str:
        """외부 노출용: 타입 메타 제거(복원 불가, 순수 JSON 형태)."""
        return jsonpickle.encode(obj, unpicklable=False, make_refs=False)

    @staticmethod
    def decode_internal(json_string: str, expected_type: Optional[Type[T]] = None) -> T:
        """내부용: 복원. expected_type이 있으면 타입 검증."""
        obj = jsonpickle.decode(json_string)
        if expected_type is not None and not isinstance(obj, expected_type):
            raise TypeError(f"Expected {expected_type.__name__}, got {type(obj).__name__}")
        return cast(T, obj)
