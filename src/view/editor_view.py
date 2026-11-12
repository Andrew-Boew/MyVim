from typing import Tuple

from src.adapter.base import ITuiAdapter
from src.model.document import TextDocument


class EditorView:
    def __init__(self, adapter: ITuiAdapter):
        self._adapter = adapter
        self._scroll_row = 0
        self._scroll_col = 0
        self._show_line_numbers = False

    def toggle_line_numbers(self) -> bool:
        self._show_line_numbers = not self._show_line_numbers
        return self._show_line_numbers

    def set_line_numbers(self, enabled: bool) -> None:
        self._show_line_numbers = enabled

    def is_line_numbers_enabled(self) -> bool:
        return self._show_line_numbers

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
        lines = doc.get_lines()
        total_lines = len(lines)

        gutter_digits = max(3, len(str(total_lines)))
        gutter_width = (gutter_digits + 1) if self._show_line_numbers else 0
        avail_width = max(1, width - gutter_width)

        cursor_row, cursor_col = doc.get_cursor()
        self._adjust_scroll(cursor_row, cursor_col, text_height, avail_width)

        self._adapter.clear()

        for screen_row in range(text_height):
            file_row = self._scroll_row + screen_row
            if file_row < total_lines:
                line_content = lines[file_row].c_str()
                if self._scroll_col < len(line_content):
                    visible_slice = line_content[self._scroll_col : self._scroll_col + avail_width]
                else:
                    visible_slice = ""
                gutter = (str(file_row + 1).rjust(gutter_digits) + " ") if self._show_line_numbers else ""
                self._adapter.add_str(screen_row, 0, gutter + visible_slice)
            else:
                gutter = (" " * gutter_width) if self._show_line_numbers else ""
                self._adapter.add_str(screen_row, 0, gutter + "~")

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
            screen_cur_col = gutter_width + cursor_col - self._scroll_col
            self._adapter.move_cursor(screen_cur_row, screen_cur_col)

        self._adapter.refresh()
