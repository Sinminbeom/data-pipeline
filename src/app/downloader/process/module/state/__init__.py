from python_library.state import StateMap

from app.downloader.process.module.state.download import DownloadState
from app.downloader.process.module.state.download_ready import DownloadReadyState
from app.downloader.process.module.state.playable import PlayableState
from app.downloader.process.module.state.state_enum import E_DOWNLOADER_MODULE_STATE
from app.downloader.process.module.state.wait import WaitState


def build_state_map() -> StateMap:
    state_map = StateMap({})
    state_map._state_map = {
        E_DOWNLOADER_MODULE_STATE.WAIT: WaitState(state_map, E_DOWNLOADER_MODULE_STATE.WAIT),
        E_DOWNLOADER_MODULE_STATE.PLAYABLE: PlayableState(state_map, E_DOWNLOADER_MODULE_STATE.PLAYABLE),
        E_DOWNLOADER_MODULE_STATE.DOWNLOAD_READY: DownloadReadyState(state_map, E_DOWNLOADER_MODULE_STATE.DOWNLOAD_READY),
        E_DOWNLOADER_MODULE_STATE.DOWNLOAD: DownloadState(state_map, E_DOWNLOADER_MODULE_STATE.DOWNLOAD),
    }
    return state_map
