from typing import Tuple

from src.adapter.base import ITuiAdapter
from src.model.document import TextDocument


class EditorView:
    def __init__(self, adapter: ITuiAdapter):
        self._adapter = adapter
        self._scroll_row = 0
        self._scroll_col = 0

    def get_adapter(self) -> ITuiAdapter:
        return self._adapter

    def get_viewport_size(self) -> Tuple[int, int]:
        height, width = self._adapter.get_size()
        text_height = max(1, height - 2)
        return text_height, width

    def _adjust_scroll(self, cursor_row: int, cursor_col: int, text_height: int, width: int) -> None:
        if cursor_row < self._scroll_row:
            self._scroll_row = cursor_row
        elif cursor_row >= self._scroll_row + text_height:
            self._scroll_row = cursor_row - text_height + 1

        if cursor_col < self._scroll_col:
            self._scroll_col = cursor_col
        elif cursor_col >= self._scroll_col + width:
            self._scroll_col = cursor_col - width + 1

    def render(
        self,
        doc: TextDocument,
        mode_name: str,
        status_message: str = "",
        command_buffer: str = "",
    ) -> None:
        height, width = self._adapter.get_size()
        if height < 3 or width < 10:
            return

        text_height = height - 2
        cursor_row, cursor_col = doc.get_cursor()
        self._adjust_scroll(cursor_row, cursor_col, text_height, width)

        self._adapter.clear()

        lines = doc.get_lines()
        total_lines = len(lines)

        for screen_row in range(text_height):
            file_row = self._scroll_row + screen_row
            if file_row < total_lines:
                line_content = lines[file_row].c_str()
                if self._scroll_col < len(line_content):
                    visible_slice = line_content[self._scroll_col : self._scroll_col + width]
                else:
                    visible_slice = ""
                self._adapter.add_str(screen_row, 0, visible_slice)
            else:
                self._adapter.add_str(screen_row, 0, "~")

        status_row = height - 2
        fname = doc.get_filename() or "[No Name]"
        mod_flag = " [+]" if doc.is_modified() else ""
        left_status = f"-- {mode_name} --  {fname}{mod_flag}"
        right_status = f"{cursor_row + 1}/{total_lines}"

        space_count = max(1, width - len(left_status) - len(right_status) - 1)
        status_line = left_status + (" " * space_count) + right_status
        self._adapter.add_str(status_row, 0, status_line[:width])

        bottom_row = height - 1
        if mode_name in ("COMMAND", "SEARCH"):
            self._adapter.add_str(bottom_row, 0, command_buffer[:width])
        else:
            if status_message:
                self._adapter.add_str(bottom_row, 0, status_message[:width])

        if mode_name in ("COMMAND", "SEARCH"):
            self._adapter.move_cursor(bottom_row, min(len(command_buffer), width - 1))
        else:
            screen_cur_row = cursor_row - self._scroll_row
            screen_cur_col = cursor_col - self._scroll_col
            self._adapter.move_cursor(screen_cur_row, screen_cur_col)

        self._adapter.refresh()
