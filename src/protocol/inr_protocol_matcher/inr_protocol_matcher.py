"""broadcast scatter-gather 응답 매처.

매니저가 N개 모듈에 broadcast REQ를 보낸 뒤, 응답 N개를 모두 받았을 때
한 번에 그룹 콜백을 발화시키기 위한 인프라. group_id 단위로 누적 + 상태 추적.

사용 흐름:
    1. broadcast 송신 직전: register_broadcast(group_id, expected_size)
    2. 응답 도착마다: append_response(group_id, packet) → 상태 반환
    3. COMPLEATE/ERROR 도달 시: get_responses(group_id)로 전체 응답 회수
    4. 처리 완료 후: clear(group_id)

group_id는 단순화를 위해 응답 protocol_id 그 자체를 사용한다 (예: INR_PLAYABLE_LIST_REP).
이는 한 시점에 동일 REP protocol_id의 outstanding broadcast가 1개라는 가정 하에 동작.
"""
from __future__ import annotations

from protocol.inr_protocol_matcher.inr_pair_state import E_PROTOCOL_PAIR_STATE
from protocol.inr_protocol_matcher.inr_protocol_container import InrProtocolContainer
from protocol.message.message import IMessage


class InrProtocolMatcher:
    def __init__(self) -> None:
        self._containers: dict[str, InrProtocolContainer] = {}

    def register_broadcast(self, group_id: str, expected_size: int) -> None:
        """broadcast 송신 직전 호출. group_id로 컨테이너 생성."""
        self._containers[group_id] = InrProtocolContainer(expected_size)

    def append_response(self, group_id: str, packet: IMessage) -> E_PROTOCOL_PAIR_STATE:
        """응답 누적 + 상태 반환. 등록 안 된 group이면 WAIT 반환 (무시)."""
        if group_id not in self._containers:
            return E_PROTOCOL_PAIR_STATE.WAIT
        container = self._containers[group_id]
        container.append(packet)
        return container.get_state()

    def get_pair_state(self, group_id: str) -> E_PROTOCOL_PAIR_STATE:
        if group_id not in self._containers:
            return E_PROTOCOL_PAIR_STATE.WAIT
        return self._containers[group_id].get_state()

    def get_responses(self, group_id: str) -> list[IMessage]:
        if group_id not in self._containers:
            return []
        return self._containers[group_id].get_responses()

    def clear(self, group_id: str) -> None:
        """그룹 콜백 발화 후 정리."""
        self._containers.pop(group_id, None)

    def has_group(self, group_id: str) -> bool:
        return group_id in self._containers
