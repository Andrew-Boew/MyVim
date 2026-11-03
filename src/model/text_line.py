import sys
from pathlib import Path
from typing import Tuple

_MYSTRING_DIR = Path(__file__).resolve().parent.parent.parent / "mystring"
if str(_MYSTRING_DIR) not in sys.path:
    sys.path.insert(0, str(_MYSTRING_DIR))

from MyString_wrapper import MyString


class TextLine:
    def __init__(self, text: str = ""):
        self._target = MyString(text)

    def size(self) -> int:
        return self._target.size()

    def __len__(self) -> int:
        return self.size()

    def c_str(self) -> str:
        return self._target.c_str()

    def __str__(self) -> str:
        return self.c_str()

    def __repr__(self) -> str:
        return f"TextLine('{self.c_str()}')"

    def at(self, index: int) -> str:
        if 0 <= index < self.size():
            val = self._target.at(index)
            return val if isinstance(val, str) else chr(val)
        return ""

    def insert(self, index: int, s: str) -> None:
        idx = max(0, min(index, self.size()))
        self._target.insert(idx, s)

    def erase(self, index: int, count: int) -> None:
        if index < 0 or index >= self.size() or count <= 0:
            return
        actual_count = min(count, self.size() - index)
        self._target.erase(index, actual_count)

    def clear(self) -> None:
        self._target.clear()

    def replace_char(self, col: int, ch: str) -> None:
        if 0 <= col < self.size() and len(ch) == 1:
            self._target.set_at(col, ch)

    def find(self, query: str, index: int = 0) -> int:
        return self._target.find(query, index)


