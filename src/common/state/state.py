from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.common.state.state_container import StateContainer


class abState(ABC):
    def __init__(self, _state_container: StateContainer):
        self._state_container: StateContainer = _state_container

        self.is_run_proc_once = False

    def get_state_manager(self):
        return self._state_container.get_state_manager()

    def get_state_component(self):
        state_manager= self.get_state_manager()
        if state_manager is not None:
            return state_manager.get_parent_state_component()

        return None

    def get_parent_class(self):
        state_manager = self.get_state_manager()
        if state_manager is None:
            return None

        state_component = state_manager.get_parent_state_component()
        if state_component is None:
            return None

        return state_component.get_parent_class()

    def base_on_enter(self):
        self.is_run_proc_once = False
        self.on_enter()

    @abstractmethod
    def on_enter(self):
        pass

    @abstractmethod
    def on_leave(self):
        pass

    @abstractmethod
    def on_proc_once(self):
        pass

    @abstractmethod
    def on_proc_every_frame(self):
        pass

    def base_on_proc_every_frame(self):
        if not self.is_run_proc_once:
            self.on_proc_once()
            self.is_run_proc_once = True

        self.on_proc_every_frame()