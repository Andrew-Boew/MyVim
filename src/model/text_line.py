import sys
from pathlib import Path
from typing import Tuple

_MYSTRING_DIR = Path(__file__).resolve().parent.parent.parent / "mystring"
if str(_MYSTRING_DIR) not in sys.path:
    sys.path.insert(0, str(_MYSTRING_DIR))

from MyString_wrapper import MyString
from src.model.word_navigator import WordNavigator


class TextLine:
    def __init__(self, text: str = ""):
        self._target = MyString(text)

    def c_str(self) -> str:
        return self._target.c_str()

    def size(self) -> int:
        return len(self.c_str())

    def __len__(self) -> int:
        return self.size()

    def __str__(self) -> str:
        return self.c_str()

    def __repr__(self) -> str:
        return f"TextLine('{self.c_str()}')"

    def at(self, index: int) -> str:
        text = self.c_str()
        if 0 <= index < len(text):
            return text[index]
        return ""

    def insert(self, index: int, s: str) -> None:
        text = self.c_str()
        char_idx = max(0, min(index, len(text)))
        byte_idx = len(text[:char_idx].encode("utf-8"))
        self._target.insert(byte_idx, s)

    def erase(self, index: int, count: int) -> None:
        text = self.c_str()
        if index < 0 or index >= len(text) or count <= 0:
            return
        actual_count = min(count, len(text) - index)
        byte_idx = len(text[:index].encode("utf-8"))
        byte_count = len(text[index:index + actual_count].encode("utf-8"))
        self._target.erase(byte_idx, byte_count)

    def clear(self) -> None:
        self._target.clear()

    def replace_char(self, col: int, ch: str) -> None:
        text = self.c_str()
        if 0 <= col < len(text) and len(ch) == 1:
            byte_idx = len(text[:col].encode("utf-8"))
            old_byte_len = len(text[col].encode("utf-8"))
            self._target.erase(byte_idx, old_byte_len)
            self._target.insert(byte_idx, ch)

    def find(self, query: str, index: int = 0) -> int:
        text = self.c_str()
        return text.find(query, index)

    def find_word_end(self, from_col: int) -> int:
        return WordNavigator.find_word_end(self, from_col)

    def find_word_start(self, from_col: int) -> int:
        return WordNavigator.find_word_start(self, from_col)

    def get_word_range_at(self, col: int) -> Tuple[int, int]:
        return WordNavigator.get_word_range_at(self, col)
