from __future__ import annotations

from typing import Generic, TypeVar

from python_library.thread.thread import abThreading

from common.process.app_process import AppProcess

ParentProcessT = TypeVar("ParentProcessT", bound=AppProcess)


class abListener(abThreading, Generic[ParentProcessT]):
    _parent_process: ParentProcessT

    def __init__(self, parent_process: ParentProcessT) -> None:
        super().__init__()
        self._parent_process = parent_process
