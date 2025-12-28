from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass, dataclass
from enum import Enum, IntEnum
from typing import Any, Mapping, Type, TypeVar

from src.define.define import E_COMMUNICATION_TYPE

T = TypeVar("T", bound="Packet")


class PacketCodecError(ValueError):
    """Raised when a packet cannot be encoded/decoded."""


def _to_primitive(obj: Any) -> Any:
    """Convert dataclasses/enums into JSON-serializable primitives."""
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Mapping):
        return {str(k): _to_primitive(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_primitive(v) for v in obj]
    return obj


class E_PROTOCOL_MESSAGE_DIRECTION(IntEnum):
    REQUEST = 0
    RESPONSE = 1
    NOTI = 2

@dataclass(frozen=True)
class Header:
    protocol_id: str
    message_direction: E_PROTOCOL_MESSAGE_DIRECTION
    communication_type: E_COMMUNICATION_TYPE
    sender: str
    receiver: str


@dataclass
class Packet:
    header: Header

    # ---- interface ----
    def to_json(self) -> str:
        """Internal serialization (typically used within your system)."""
        raise NotImplementedError

    def to_json_public(self) -> str:
        """External/wire serialization (typically used for integration)."""
        raise NotImplementedError

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        raise NotImplementedError

    # ---- shared helpers ----
    @staticmethod
    def _encode_internal(obj: Any) -> str:
        """Best-effort internal encoding using JsonpickleUtil, fallback to json."""
        try:
            # 프로젝트 내 공용 유틸이 있다면 최우선 사용
            from src.utils.jsonpickle_util import JsonpickleUtil  # type: ignore

            return JsonpickleUtil.encode_internal(obj)
        except Exception:
            try:
                return json.dumps(_to_primitive(obj), ensure_ascii=False, separators=(",", ":"))
            except Exception as e:
                raise PacketCodecError("Failed to encode packet (internal).") from e

    @staticmethod
    def _encode_external(obj: Any) -> str:
        """Best-effort external encoding using JsonpickleUtil, fallback to json."""
        try:
            from src.utils.jsonpickle_util import JsonpickleUtil  # type: ignore

            return JsonpickleUtil.encode_external(obj)
        except Exception:
            try:
                return json.dumps(_to_primitive(obj), ensure_ascii=False, separators=(",", ":"))
            except Exception as e:
                raise PacketCodecError("Failed to encode packet (external).") from e

    @staticmethod
    def _decode_internal(expected_type: Type[T], json_data: str) -> T:
        """Best-effort internal decoding using JsonpickleUtil, fallback to kwargs."""
        try:
            from src.utils.jsonpickle_util import JsonpickleUtil  # type: ignore

            return JsonpickleUtil.decode_internal(json_data, expected_type=expected_type)
        except Exception:
            try:
                raw = json.loads(json_data)
            except Exception as e:
                raise PacketCodecError("Invalid JSON.") from e

            if not isinstance(raw, Mapping):
                raise PacketCodecError("JSON root must be an object.")

            try:
                return expected_type(**raw)  # type: ignore[arg-type]
            except Exception as e:
                raise PacketCodecError(f"Failed to decode into {expected_type.__name__}.") from e
