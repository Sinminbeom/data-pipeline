from __future__ import annotations

from abc import abstractmethod
from enum import Enum
import time
from typing import Optional

from python_library.logger.app_logger import AppLogger
from python_library.process.queue_process import QueueProcess
from python_library.state import StateComponent, StateMap

from config.project_config import ProjectConfig


class StepProcess(QueueProcess):
    def __init__(self, app_name: str, process_name: str) -> None:
        super().__init__(process_name)
        self._app_name = app_name

        self._state_component: Optional[StateComponent] = None

    def _set_config(self) -> None:
        AppLogger.set_config(ProjectConfig.DEFAULT_CONFIG_PATH, self.name)
        ProjectConfig.set_config(ProjectConfig.DEFAULT_CONFIG_PATH)

    def get_app_name(self) -> str:
        return self._app_name

    def set_state_component(
        self,
        state_map: StateMap,
        init_state_id: Enum,
    ) -> None:
        self._state_component = StateComponent(
            owner=self,
            state_map=state_map,
            init_state_id=init_state_id,
        )

    def action(self) -> None:
        self._set_config()
        self.on_init()
        self.on_proc_once()

        try:
            while self.is_running():
                if self._state_component is not None:
                    self._state_component.on_change_state()

                self.on_proc_every_frame()

                if self._state_component is not None:
                    self._state_component.on_proc_every_frame()

                time.sleep(0.001)
        except Exception as e:
            raise e

    @abstractmethod
    def on_init(self):
        raise NotImplementedError

    @abstractmethod
    def on_proc_once(self):
        raise NotImplementedError

    @abstractmethod
    def on_proc_every_frame(self):
        raise NotImplementedError
