from src.common.state.state import abState
from src.common.state.state_manager import StateManager


class StateContainer:
    def __init__(self, states: dict[str, abState]) -> None:
        self._states = states
        self.state_manager: StateManager | None = None

    def set_states(self, states: dict[str, abState]) -> None:
        self._states = states

    def get_state(self, state_key: str) -> abState:
        return self._states[state_key]

    def set_state_manager(self, state_manager: StateManager) -> None:
        self.state_manager = state_manager

    def get_state_manager(self) -> StateManager | None:
        return self.state_manager