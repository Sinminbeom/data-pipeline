from dataclasses import dataclass
from typing import Generic, Optional

from src.common.state.types import TKey


@dataclass(frozen=True)
class ChangeResult(Generic[TKey]):
    prev: Optional[TKey]
    curr: TKey