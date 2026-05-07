from python_library.state import StateMap

from app.streamer.process.module.state.play import PlayState
from app.streamer.process.module.state.state_enum import E_STREAMER_MODULE_STATE
from app.streamer.process.module.state.wait import WaitState


def build_state_map() -> StateMap:
    state_map = StateMap({})
    state_map._state_map = {
        E_STREAMER_MODULE_STATE.WAIT: WaitState(state_map, E_STREAMER_MODULE_STATE.WAIT),
        E_STREAMER_MODULE_STATE.PLAY: PlayState(state_map, E_STREAMER_MODULE_STATE.PLAY),
    }
    return state_map
