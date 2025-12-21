from __future__ import annotations

from typing import TYPE_CHECKING

from src.common.state.state import abState

if TYPE_CHECKING:
    from src.common.state.state_component import StateComponent
    from src.common.state.state_container import StateContainer


class StateManager:
    def __init__(self, state_container: StateContainer, parent_state_component: StateComponent) -> None:
        self._state_container: StateContainer = state_container
        self._parent_state_component: StateComponent = parent_state_component

        self._set_state_container()

        self.current_state_key: str | None = None

    def _set_state_container(self):
        self._state_container.set_state_manager(self)

    def get_parent_state_component(self):
        return self._parent_state_component

    def get_state(self, state) -> abState:
        return self._state_container.get_state(state)

    def change_state(self, _state_key: str) -> abState | None:
        if self.current_state_key is not None:
            self.get_state(self.current_state_key).on_leave()

        self.current_state_key = _state_key
        self.get_state(_state_key).base_on_enter()

        return self._state_container.get_state(self.current_state_key)

    def get_current_state(self) -> abState | None:
        if self.current_state_key is None:
            return None

        return self._state_container.get_state(self.current_state_key)