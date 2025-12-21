from process.process import abProcess
from abc import abstractmethod

from src.common.state.state_component import StateComponent
from src.common.state.state_container import StateContainer


# TODO: state_component 구현
class StepProcess(abProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(process_name)
        self._app_name = app_name

        self._state_component : StateComponent | None = None

    def get_app_name(self) -> str:
        return self._app_name

    def set_state_component(self, state_container: StateContainer, init_state_key: str) -> None:
        self._state_component = StateComponent(self, state_container, init_state_key)

    def action(self) -> None:
        self.on_init()
        self.on_proc_once()

        try:
            while self.is_running():
                self.on_proc_once()

                if self._state_component is not None:
                    self._state_component.on_proc_every_frame()
                    self._state_component.on_change_state()

        except Exception as e:
            self.stop()
            raise Exception(e)
        pass

    @abstractmethod
    def on_init(self):
        raise NotImplementedError

    @abstractmethod
    def on_proc_once(self):
        raise NotImplementedError

    @abstractmethod
    def on_proc_every_frame(self):
        raise NotImplementedError

