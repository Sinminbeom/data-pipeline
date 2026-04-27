from enum import IntEnum


class E_DOWNLOADER_MANAGER_STATE(IntEnum):
    WAIT = 0
    PLAYABLE = 1
    DOWNLOAD_READY = 2
    DOWNLOAD = 3
    STOP = 4
    CLOSE = 5
    SEEK = 6
    ERROR = 7
