from typing import List, Tuple

from src.adapter.base import ITuiAdapter


class MockTuiAdapter(ITuiAdapter):
    def __init__(self, rows: int = 24, cols: int = 80):
        self.rows = rows
        self.cols = cols
        self.cursor_row = 0
        self.cursor_col = 0
        self.cursor_visible = True
        self.is_initialized = False

        self._screen: List[List[str]] = [[" " for _ in range(cols)] for _ in range(rows)]
        self._input_queue: List[int] = []
        self.refresh_count = 0

    def feed_input(self, keys: List[int]) -> None:
        self._input_queue.extend(keys)

    def initialize(self) -> None:
        self.is_initialized = True
        self.clear()

    def shutdown(self) -> None:
        self.is_initialized = False

    def get_size(self) -> Tuple[int, int]:
        return self.rows, self.cols

    def move_cursor(self, row: int, col: int) -> None:
        self.cursor_row = max(0, min(row, self.rows - 1))
        self.cursor_col = max(0, min(col, self.cols - 1))

    def set_cursor_visibility(self, visible: bool) -> None:
        self.cursor_visible = visible

    def add_str(self, row: int, col: int, text: str, attr: int = 0) -> None:
        if 0 <= row < self.rows:
            for i, ch in enumerate(text):
                target_col = col + i
                if 0 <= target_col < self.cols:
                    self._screen[row][target_col] = ch

    def clear_line(self, row: int) -> None:
        if 0 <= row < self.rows:
            self._screen[row] = [" " for _ in range(self.cols)]

    def clear(self) -> None:
        self._screen = [[" " for _ in range(self.cols)] for _ in range(self.rows)]

    def refresh(self) -> None:
        self.refresh_count += 1

    def get_key(self) -> int:
        if self._input_queue:
            return self._input_queue.pop(0)
        return -1

    def get_line_text(self, row: int) -> str:
        if 0 <= row < self.rows:
            return "".join(self._screen[row]).rstrip()
        return ""

    def get_screen_lines(self) -> List[str]:
        return [self.get_line_text(r) for r in range(self.rows)]
