from src.common.state.state_container import StateContainer
from src.common.state.state_manager import StateManager


class StateComponent:
    def __init__(self, parent_class: object, state_container: StateContainer, init_state_key: str) -> None:
        self._parent_class = parent_class
        self._state_container = state_container
        self._init_state_key = init_state_key

        self.state_manager = StateManager(state_container, self)
        self.reserve_state_key: str | None = None

        if init_state_key is not None:
            self.change_state(init_state_key)
            self.on_change_state()

    def get_parent_class(self) -> object:
        return self._parent_class

    def change_state(self, new_state_key: str) -> None:
        self.reserve_state_key = new_state_key

    def on_change_state(self):
        if self.reserve_state_key is not None:
            self.state_manager.change_state(self.reserve_state_key)
            self.reserve_state_key = None

    def on_proc_once(self):
        current_state = self.state_manager.get_current_state()

        if current_state is not None:
            current_state.on_proc_once()

    def on_proc_every_frame(self):
        current_state = self.state_manager.get_current_state()

        if current_state is not None:
            current_state.base_on_proc_every_frame()
