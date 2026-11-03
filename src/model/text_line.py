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

    def find_word_end(self, from_col: int) -> int:
        text = self.c_str()
        length = len(text)
        if length == 0:
            return 0
        if from_col >= length - 1:
            return max(0, length - 1)

        idx = from_col
        if not text[idx].isspace():
            is_alnum = text[idx].isalnum()
            end_current = idx
            while (
                end_current + 1 < length
                and not text[end_current + 1].isspace()
                and text[end_current + 1].isalnum() == is_alnum
            ):
                end_current += 1
            if idx < end_current:
                return end_current
            idx = end_current + 1

        while idx < length and text[idx].isspace():
            idx += 1

        if idx >= length:
            return length - 1

        next_alnum = text[idx].isalnum()
        end_next = idx
        while (
            end_next + 1 < length
            and not text[end_next + 1].isspace()
            and text[end_next + 1].isalnum() == next_alnum
        ):
            end_next += 1

        return end_next

    def find_word_start(self, from_col: int) -> int:
        text = self.c_str()
        length = len(text)
        if length == 0 or from_col <= 0:
            return 0

        idx = min(from_col, length - 1)
        if not text[idx].isspace():
            is_alnum = text[idx].isalnum()
            start_current = idx
            while (
                start_current > 0
                and not text[start_current - 1].isspace()
                and text[start_current - 1].isalnum() == is_alnum
            ):
                start_current -= 1
            if start_current < idx:
                return start_current
            idx = start_current - 1

        while idx >= 0 and text[idx].isspace():
            idx -= 1

        if idx <= 0:
            return 0

        prev_alnum = text[idx].isalnum()
        start_prev = idx
        while (
            start_prev > 0
            and not text[start_prev - 1].isspace()
            and text[start_prev - 1].isalnum() == prev_alnum
        ):
            start_prev -= 1

        return start_prev

    def get_word_range_at(self, col: int) -> Tuple[int, int]:
        text = self.c_str()
        length = len(text)
        if length == 0 or col < 0 or col >= length:
            return 0, 0

        start = col
        is_alnum = text[col].isalnum()
        is_space = text[col].isspace()

        while start > 0:
            prev = text[start - 1]
            if is_space:
                if not prev.isspace():
                    break
            else:
                if prev.isspace() or prev.isalnum() != is_alnum:
                    break
            start -= 1

        end = col
        while end < length:
            curr = text[end]
            if is_space:
                if not curr.isspace():
                    break
            else:
                if curr.isspace() or curr.isalnum() != is_alnum:
                    break
            end += 1

        while end < length and text[end].isspace():
            end += 1

        return start, end
