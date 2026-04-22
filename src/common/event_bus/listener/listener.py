from abc import abstractmethod

from python_library.process.process import abProcess
from python_library.thread.thread import abThreading


class abListener(abThreading):
    def __init__(self, _parent_process: abProcess) -> None:
        super().__init__()
        self._parent_process: abProcess = _parent_process

    @abstractmethod
    def action(self) -> None:
        pass