from python_library.state import StateMap

from app.streamer.process.manager.state.pause import PauseState
from app.streamer.process.manager.state.play import PlayState
from app.streamer.process.manager.state.seek import SeekState
from app.streamer.process.manager.state.state_enum import E_STREAMER_MANAGER_STATE
from app.streamer.process.manager.state.wait import WaitState


def build_state_map() -> StateMap:
    state_map = StateMap({})
    state_map._state_map = {
        E_STREAMER_MANAGER_STATE.WAIT: WaitState(state_map, E_STREAMER_MANAGER_STATE.WAIT),
        E_STREAMER_MANAGER_STATE.PLAY: PlayState(state_map, E_STREAMER_MANAGER_STATE.PLAY),
        E_STREAMER_MANAGER_STATE.PAUSE: PauseState(state_map, E_STREAMER_MANAGER_STATE.PAUSE),
        E_STREAMER_MANAGER_STATE.SEEK: SeekState(state_map, E_STREAMER_MANAGER_STATE.SEEK),
    }
    return state_map
