from typing import List, Optional, Tuple

from src.model.text_line import TextLine


class TextDocument:
    def __init__(self, text: str = ""):
        self._lines: List[TextLine] = []
        self._cursor_row = 0
        self._cursor_col = 0
        self._desired_col = 0
        self._filename: Optional[str] = None
        self._is_modified = False
        self._clipboard = ""
        self._clipboard_is_line = False
        self._undo_stack: List[dict] = []
        self._last_search_query = ""
        self._last_search_forward = True

        if text:
            self.set_text(text)
        else:
            self._lines = [TextLine("")]

    def get_lines(self) -> List[TextLine]:
        return self._lines

    def get_line_count(self) -> int:
        return len(self._lines)

    def get_line(self, row: int) -> TextLine:
        if 0 <= row < len(self._lines):
            return self._lines[row]
        return self._lines[-1]

    def get_cursor(self) -> Tuple[int, int]:
        return self._cursor_row, self._cursor_col

    def set_cursor(self, row: int, col: int) -> None:
        self._cursor_row = max(0, min(row, max(0, len(self._lines) - 1)))
        line_len = len(self._lines[self._cursor_row])
        self._cursor_col = max(0, min(col, line_len))
        self._desired_col = self._cursor_col

    def get_filename(self) -> Optional[str]:
        return self._filename

    def set_filename(self, filename: Optional[str]) -> None:
        self._filename = filename

    def is_modified(self) -> bool:
        return self._is_modified

    def set_modified(self, modified: bool) -> None:
        self._is_modified = modified

    def get_clipboard(self) -> str:
        return self._clipboard

    def is_clipboard_line(self) -> bool:
        return self._clipboard_is_line

    def set_clipboard(self, text: str, is_line: bool = False) -> None:
        self._clipboard = text
        self._clipboard_is_line = is_line

    def set_text(self, text: str) -> None:
        raw_lines = text.splitlines()
        if not raw_lines:
            self._lines = [TextLine("")]
        else:
            self._lines = [TextLine(line) for line in raw_lines]
        self._cursor_row = 0
        self._cursor_col = 0
        self._desired_col = 0
        self._is_modified = False
        self._undo_stack.clear()

    def get_text(self) -> str:
        return "\n".join(line.c_str() for line in self._lines)

    def load(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        self.set_text(content)
        self._filename = filepath
        self._is_modified = False

    def save(self, filepath: Optional[str] = None) -> None:
        target_path = filepath or self._filename
        if not target_path:
            raise ValueError("No filename specified")
        content = self.get_text()
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        self._filename = target_path
        self._is_modified = False


