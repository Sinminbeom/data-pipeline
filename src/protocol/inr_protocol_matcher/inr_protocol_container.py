from __future__ import annotations

from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.message.message import IMessage


class InrProtocolContainer:
    """단일 broadcast group의 응답 누적 + 상태 추적.

    broadcast 시점에 expected_size 등록 → 응답 도착할 때마다 append →
    누적 수가 expected_size에 도달하면 COMPLEATE. 응답 중 하나라도 에러면 ERROR.
    """

    def __init__(self, expected_size: int) -> None:
        self._expected_size = expected_size
        self._responses: list[IMessage] = []
        self._has_error = False

    def append(self, packet: IMessage) -> None:
        self._responses.append(packet)
        # response는 abImdgResponseMessage / abProcessResponseMessage에만 있음.
        # 컨테이너 시그니처는 IMessage 유지 — runtime attribute lookup으로 정상 케이스 처리.
        response = getattr(packet, "response", None)
        if response is not None and response.code not in ("", "OK"):
            self._has_error = True

    def get_state(self) -> E_PROTOCOL_PAIR_STATE:
        if self._has_error:
            return E_PROTOCOL_PAIR_STATE.ERROR
        if len(self._responses) >= self._expected_size:
            return E_PROTOCOL_PAIR_STATE.COMPLEATE
        return E_PROTOCOL_PAIR_STATE.WAIT

    def get_responses(self) -> list[IMessage]:
        return list(self._responses)

    def __repr__(self) -> str:
        return (
            f"InrProtocolContainer(expected={self._expected_size}, "
            f"received={len(self._responses)}, state={self.get_state().name})"
        )
