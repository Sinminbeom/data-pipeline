from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TYPE_CHECKING

from src.common.state.types import TOwner, TKey
if TYPE_CHECKING:
    from src.common.state.state_machine import StateMachine


class abState(ABC, Generic[TOwner, TKey]):
    """
    State lifecycle:
      - on_enter: called once when this state becomes current
      - on_leave: called once when this state is replaced
      - on_proc_once: called once on first update after entering
      - on_proc_every_frame: called every update while current
    """

    def __init__(self) -> None:
        self._has_run_once: bool = False

    @property
    def has_run_once(self) -> bool:
        return self._has_run_once

    def _reset_once_flag(self) -> None:
        self._has_run_once = False

    def _mark_once_ran(self) -> None:
        self._has_run_once = True

    @abstractmethod
    def on_enter(self, owner: TOwner, machine: StateMachine[TOwner, TKey]) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_leave(self, owner: TOwner, machine: StateMachine[TOwner, TKey]) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_proc_once(self, owner: TOwner, machine: StateMachine[TOwner, TKey]) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_proc_every_frame(
        self,
        owner: TOwner,
        machine: StateMachine[TOwner, TKey]
    ) -> None:
        raise NotImplementedError