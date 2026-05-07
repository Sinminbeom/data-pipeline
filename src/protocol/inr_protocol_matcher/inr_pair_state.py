from enum import IntEnum


class E_PROTOCOL_PAIR_STATE(IntEnum):
    """broadcast group의 누적 상태."""
    WAIT = 0        # 아직 응답 누적 중
    COMPLEATE = 1   # 기대한 응답 수만큼 도착
    ERROR = 2       # 응답 중 하나가 에러 코드를 담아 도착
