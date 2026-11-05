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

    def move_cursor_left(self) -> None:
        if self._cursor_col > 0:
            self._cursor_col -= 1
            self._desired_col = self._cursor_col

    def move_cursor_right(self, allow_past_end: bool = False) -> None:
        line_len = len(self._lines[self._cursor_row])
        max_col = line_len if allow_past_end else max(0, line_len - 1)
        if self._cursor_col < max_col:
            self._cursor_col += 1
            self._desired_col = self._cursor_col

    def move_cursor_up(self) -> None:
        if self._cursor_row > 0:
            self._cursor_row -= 1
            line_len = len(self._lines[self._cursor_row])
            self._cursor_col = min(self._desired_col, max(0, line_len - 1))

    def move_cursor_down(self) -> None:
        if self._cursor_row < len(self._lines) - 1:
            self._cursor_row += 1
            line_len = len(self._lines[self._cursor_row])
            self._cursor_col = min(self._desired_col, max(0, line_len - 1))

    def move_cursor_line_start(self) -> None:
        self._cursor_col = 0
        self._desired_col = 0

    def move_cursor_line_end(self) -> None:
        line_len = len(self._lines[self._cursor_row])
        self._cursor_col = max(0, line_len - 1)
        self._desired_col = self._cursor_col

    def move_cursor_word_forward(self) -> None:
        line = self._lines[self._cursor_row]
        line_len = len(line)
        if self._cursor_col < line_len - 1:
            target = line.find_word_end(self._cursor_col)
            if target > self._cursor_col:
                self._cursor_col = target
                self._desired_col = target
                return
        if self._cursor_row < len(self._lines) - 1:
            self._cursor_row += 1
            next_line = self._lines[self._cursor_row]
            target = next_line.find_word_end(0)
            self._cursor_col = target
            self._desired_col = target

    def move_cursor_word_backward(self) -> None:
        if self._cursor_col > 0:
            line = self._lines[self._cursor_row]
            target = line.find_word_start(self._cursor_col)
            if target < self._cursor_col:
                self._cursor_col = target
                self._desired_col = target
                return
        if self._cursor_row > 0:
            self._cursor_row -= 1
            prev_line = self._lines[self._cursor_row]
            prev_len = len(prev_line)
            target = prev_line.find_word_start(max(0, prev_len - 1))
            self._cursor_col = target
            self._desired_col = target

    def move_cursor_file_start(self) -> None:
        self._cursor_row = 0
        self._cursor_col = 0
        self._desired_col = 0

    def move_cursor_file_end(self) -> None:
        self._cursor_row = max(0, len(self._lines) - 1)
        line_len = len(self._lines[self._cursor_row])
        self._cursor_col = min(self._desired_col, max(0, line_len - 1))

    def move_cursor_to_line(self, line_number: int) -> None:
        target_row = max(0, min(line_number - 1, len(self._lines) - 1))
        self._cursor_row = target_row
        line_len = len(self._lines[self._cursor_row])
        self._cursor_col = min(self._desired_col, max(0, line_len - 1))

    def page_up(self, page_size: int = 20) -> None:
        self._cursor_row = max(0, self._cursor_row - page_size)
        line_len = len(self._lines[self._cursor_row])
        self._cursor_col = min(self._desired_col, max(0, line_len - 1))

    def page_down(self, page_size: int = 20) -> None:
        self._cursor_row = min(max(0, len(self._lines) - 1), self._cursor_row + page_size)
        line_len = len(self._lines[self._cursor_row])
        self._cursor_col = min(self._desired_col, max(0, line_len - 1))

    def delete_char(self) -> None:
        line = self._lines[self._cursor_row]
        if len(line) == 0 or self._cursor_col >= len(line):
            return
        self.record_snapshot()
        self._clipboard = line.at(self._cursor_col)
        self._clipboard_is_line = False
        line.erase(self._cursor_col, 1)
        if self._cursor_col >= len(line) and self._cursor_col > 0:
            self._cursor_col = len(line) - 1
        self._desired_col = self._cursor_col
        self._is_modified = True

    def replace_char(self, char: str) -> None:
        line = self._lines[self._cursor_row]
        if len(line) > 0 and 0 <= self._cursor_col < len(line) and len(char) == 1:
            self.record_snapshot()
            line.replace_char(self._cursor_col, char)
            self._is_modified = True

    def clear_current_line(self) -> None:
        self.record_snapshot()
        self._lines[self._cursor_row] = TextLine("")
        self._cursor_col = 0
        self._desired_col = 0
        self._is_modified = True

    def open_line_below(self) -> None:
        self.record_snapshot()
        insert_idx = self._cursor_row + 1
        self._lines.insert(insert_idx, TextLine(""))
        self._cursor_row = insert_idx
        self._cursor_col = 0
        self._desired_col = 0
        self._is_modified = True

    def open_line_above(self) -> None:
        self.record_snapshot()
        self._lines.insert(self._cursor_row, TextLine(""))
        self._cursor_col = 0
        self._desired_col = 0
        self._is_modified = True

    def insert_text(self, text: str) -> None:
        self.record_snapshot()
        line = self._lines[self._cursor_row]
        insert_pos = min(self._cursor_col, len(line))
        line.insert(insert_pos, text)
        self._cursor_col = insert_pos + len(text)
        self._desired_col = self._cursor_col
        self._is_modified = True

    def split_line(self) -> None:
        self.record_snapshot()
        cur_line = self._lines[self._cursor_row]
        cur_text = cur_line.c_str()
        split_idx = min(self._cursor_col, len(cur_line))
        left_part = cur_text[:split_idx]
        right_part = cur_text[split_idx:]
        self._lines[self._cursor_row] = TextLine(left_part)
        new_line = TextLine(right_part)
        self._lines.insert(self._cursor_row + 1, new_line)
        self._cursor_row += 1
        self._cursor_col = 0
        self._desired_col = 0
        self._is_modified = True

    def backspace(self) -> None:
        if self._cursor_col > 0:
            self.record_snapshot()
            line = self._lines[self._cursor_row]
            line.erase(self._cursor_col - 1, 1)
            self._cursor_col -= 1
            self._desired_col = self._cursor_col
            self._is_modified = True
        elif self._cursor_row > 0:
            self.record_snapshot()
            prev_line = self._lines[self._cursor_row - 1]
            prev_len = len(prev_line)
            curr_line = self._lines[self._cursor_row]
            prev_line.insert(prev_len, curr_line.c_str())
            del self._lines[self._cursor_row]
            self._cursor_row -= 1
            self._cursor_col = prev_len
            self._desired_col = prev_len
            self._is_modified = True


