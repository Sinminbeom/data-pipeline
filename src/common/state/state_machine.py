from typing import Generic, Optional

from src.common.state.change_result import ChangeResult
from src.common.state.state import TOwner, TKey, abState
from src.common.state.state_container import StateContainer


class StateMachine(Generic[TOwner, TKey]):
    def __init__(
        self,
        owner: TOwner,
        states: StateContainer[TOwner, TKey],
        initial: TKey,
    ) -> None:
        if initial not in states:
            raise KeyError(f"Initial state key not found: {initial}")

        self.owner: TOwner = owner
        self.states: StateContainer[TOwner, TKey] = states

        self.current_key: Optional[TKey] = None
        self.current_state: Optional[abState[TOwner, TKey]] = None

        # enter initial
        self.change(initial)

    def change(self, next_key: TKey) -> ChangeResult[TKey]:
        if next_key not in self.states:
            raise KeyError(f"State key not found: {next_key}")

        prev_key = self.current_key
        prev_state = self.current_state

        if prev_state is not None:
            prev_state.on_leave(self.owner, self)

        next_state = self.states[next_key]
        next_state._reset_once_flag()

        self.current_key = next_key
        self.current_state = next_state

        next_state.on_enter(self.owner, self)

        return ChangeResult(prev=prev_key, curr=next_key)

    def update(self) -> None:

        def _run_once_if_needed(s: abState[TOwner, TKey]) -> None:
            if not s.has_run_once:
                s.on_proc_once(self.owner, self)
                s._mark_once_ran()

        state = self.current_state
        if state is None:
            return

        before = state

        # 1) Run once for the current state (if needed)
        _run_once_if_needed(state)

        # 2) If state changed during once, immediately process the new state (once + tick) and stop
        if self.current_state is not before:
            state = self.current_state
            if state is None:
                return

            _run_once_if_needed(state)
            state.on_proc_every_frame(self.owner, self)
            return

        # 3) Normal tick path
        state.on_proc_every_frame(self.owner, self)

    def is_current(self, key: TKey) -> bool:
        return self.current_key == key
