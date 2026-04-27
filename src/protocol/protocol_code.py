from enum import IntEnum

from protocol.message.message import ResponseInfo


class E_CODE(IntEnum):
    OK = 0
    INVALID_REQUEST = 1


_CODE_META = {
    E_CODE.OK: ("OK", ""),
    E_CODE.INVALID_REQUEST: ("INVALID_REQUEST", "current state does not allow this request"),
}


def make_response_info(code: E_CODE, reason: str | None = None) -> ResponseInfo:
    name, default_reason = _CODE_META[code]
    return ResponseInfo(
        code=name,
        code_nm=name,
        reason=reason if reason is not None else default_reason,
    )
