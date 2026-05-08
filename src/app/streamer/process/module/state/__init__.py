from python_library.state import StateMap

from app.streamer.process.module.state.close import CloseState
from app.streamer.process.module.state.pause import PauseState
from app.streamer.process.module.state.play import PlayState
from app.streamer.process.module.state.seek import SeekState
from app.streamer.process.module.state.state_enum import E_STREAMER_MODULE_STATE
from app.streamer.process.module.state.stop import StopState
from app.streamer.process.module.state.wait import WaitState


def build_state_map() -> StateMap:
    state_map = StateMap({})
    state_map._state_map = {
        E_STREAMER_MODULE_STATE.WAIT: WaitState(state_map, E_STREAMER_MODULE_STATE.WAIT),
        E_STREAMER_MODULE_STATE.PLAY: PlayState(state_map, E_STREAMER_MODULE_STATE.PLAY),
        E_STREAMER_MODULE_STATE.PAUSE: PauseState(state_map, E_STREAMER_MODULE_STATE.PAUSE),
        E_STREAMER_MODULE_STATE.SEEK: SeekState(state_map, E_STREAMER_MODULE_STATE.SEEK),
        E_STREAMER_MODULE_STATE.CLOSE: CloseState(state_map, E_STREAMER_MODULE_STATE.CLOSE),
        E_STREAMER_MODULE_STATE.STOP: StopState(state_map, E_STREAMER_MODULE_STATE.STOP),
    }
    return state_map
