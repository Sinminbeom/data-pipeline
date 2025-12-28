from __future__ import annotations

from typing import List, Any


class StringBuilder:
    def __init__(self) -> None:
        self._strings: List[str] = []

    def append(self, value: Any) -> StringBuilder:
        """
        Append any value after converting it to str.

        Time complexity:
          - append: amortized O(1)
        """
        self._strings.append(str(value))
        return self

    def to_string(self) -> str:
        """
        Build final string.

        Time complexity:
          - join: O(n) where n is total length of all parts
        """
        return "".join(self._strings)

    def clear(self) -> None:
        self._strings.clear()

    def __str__(self) -> str:
        return self.to_string()

    def __len__(self) -> int:
        return len(self._strings)
