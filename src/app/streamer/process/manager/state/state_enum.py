from enum import IntEnum


class E_STREAMER_MANAGER_STATE(IntEnum):
    WAIT = 0
    PLAY = 1
    PAUSE = 2
    SEEK = 3
    CLOSE = 4
