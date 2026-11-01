from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Tuple


class KeyCode(IntEnum):
    ESC = 27
    ENTER = 10
    RETURN = 13
    BACKSPACE = 127
    KEY_BACKSPACE = 263
    TAB = 9

    UP = 1001
    DOWN = 1002
    LEFT = 1003
    RIGHT = 1004
    PAGE_UP = 1005
    PAGE_DOWN = 1006
    HOME = 1007
    END = 1008
    DELETE = 1009


class ITuiAdapter(ABC):
    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass

    @abstractmethod
    def get_size(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def move_cursor(self, row: int, col: int) -> None:
        pass

    @abstractmethod
    def set_cursor_visibility(self, visible: bool) -> None:
        pass

    @abstractmethod
    def add_str(self, row: int, col: int, text: str, attr: int = 0) -> None:
        pass

    @abstractmethod
    def clear_line(self, row: int) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def refresh(self) -> None:
        pass

    @abstractmethod
    def get_key(self) -> int:
        pass
