from process.process import abProcess
from abc import abstractmethod
import time

from src.common.state.state_container import StateContainer
from src.common.state.state_machine import StateMachine


class StepProcess(abProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(process_name)
        self._app_name = app_name

        self._state_machine: StateMachine | None = None

    def get_app_name(self) -> str:
        return self._app_name

    def set_state_machine(self, state_container: StateContainer, init_state_key: str) -> None:
        self._state_machine = StateMachine(self, state_container, init_state_key)

    def action(self) -> None:
        self.on_init()
        self.on_proc_once()

        try:
            while self.is_running():
                self.on_proc_every_frame()

                if self._state_machine is not None:
                    self._state_machine.update()

                time.sleep(0.001)
        except Exception as e:
            raise e
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

