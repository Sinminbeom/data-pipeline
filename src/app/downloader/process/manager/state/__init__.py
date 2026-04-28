from python_library.state import StateMap

from app.downloader.process.manager.state.state_enum import E_DOWNLOADER_MANAGER_STATE
from app.downloader.process.manager.state.wait import WaitState
from app.downloader.process.manager.state.playable import PlayableState


def build_state_map() -> StateMap:
    state_map = StateMap({})
    state_map._state_map = {
        E_DOWNLOADER_MANAGER_STATE.WAIT: WaitState(state_map, E_DOWNLOADER_MANAGER_STATE.WAIT),
        E_DOWNLOADER_MANAGER_STATE.PLAYABLE: PlayableState(state_map, E_DOWNLOADER_MANAGER_STATE.PLAYABLE),
    }
    return state_map
