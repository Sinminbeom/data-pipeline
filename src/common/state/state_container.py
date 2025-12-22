from collections.abc import Mapping
from typing import Iterator, Dict

from src.common.state.state import TKey, abState, TOwner


class StateContainer(Mapping[TKey, abState[TOwner, TKey]]):
    def __init__(self, state: Dict[TKey, abState[TOwner, TKey]]) -> None:
        self._states: Dict[TKey, abState[TOwner, TKey]] = state

    def __getitem__(self, key: TKey) -> abState[TOwner, TKey]:
        return self._states[key]

    def __iter__(self) -> Iterator[TKey]:
        return iter(self._states)

    def __len__(self) -> int:
        return len(self._states)
