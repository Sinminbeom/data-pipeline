from enum import IntEnum


class E_DOWNLOADER_MODULE_STATE(IntEnum):
    WAIT = 0
    PLAYABLE = 1
    DOWNLOAD_READY = 2
    DOWNLOAD = 3
    SEEK = 4
    COMPLETED = 5
    STOP = 6
    CLOSE = 7
