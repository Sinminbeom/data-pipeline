from __future__ import annotations

from typing import Generic, TypeVar

from common.event_bus.listener.listener import abListener
from common.process.app_process import AppProcess

ParentProcessT = TypeVar("ParentProcessT", bound=AppProcess)


class abEventBus(Generic[ParentProcessT]):
    _parent_process: ParentProcessT
    listener: abListener | None

    def __init__(self, parent_process: ParentProcessT) -> None:
        self._parent_process = parent_process
        self.listener = None

    def start(self):
        self.listener.start()
