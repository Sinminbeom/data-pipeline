from common.state.state_container import StateContainer

from app.downloader.process.manager.state.state_enum import E_DOWNLOADER_MANAGER_STATE
from app.downloader.process.manager.state.wait import WaitState
from app.downloader.process.manager.state.playable import PlayableState


def build_state_container() -> StateContainer:
    return StateContainer({
        E_DOWNLOADER_MANAGER_STATE.WAIT: WaitState(),
        E_DOWNLOADER_MANAGER_STATE.PLAYABLE: PlayableState(),
    })
