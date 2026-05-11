from python_library.state import StateMap

from app.downloader.process.manager.state.download import DownloadState
from app.downloader.process.manager.state.download_ready import DownloadReadyState
from app.downloader.process.manager.state.playable import PlayableState
from app.downloader.process.manager.state.state_enum import E_DOWNLOADER_MANAGER_STATE
from app.downloader.process.manager.state.wait import WaitState


def build_state_map() -> StateMap:
    state_map = StateMap({})
    state_map._state_map = {
        E_DOWNLOADER_MANAGER_STATE.WAIT: WaitState(state_map, E_DOWNLOADER_MANAGER_STATE.WAIT),
        E_DOWNLOADER_MANAGER_STATE.PLAYABLE: PlayableState(state_map, E_DOWNLOADER_MANAGER_STATE.PLAYABLE),
        E_DOWNLOADER_MANAGER_STATE.DOWNLOAD_READY: DownloadReadyState(state_map, E_DOWNLOADER_MANAGER_STATE.DOWNLOAD_READY),
        E_DOWNLOADER_MANAGER_STATE.DOWNLOAD: DownloadState(state_map, E_DOWNLOADER_MANAGER_STATE.DOWNLOAD),
    }
    return state_map
