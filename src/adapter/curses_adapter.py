import curses
import os
from typing import Optional, Tuple

from src.adapter.base import ITuiAdapter, KeyCode


class CursesAdapter(ITuiAdapter):
    def __init__(self, stdscr: Optional["curses.window"] = None):
        self._stdscr = stdscr
        self._owns_screen = stdscr is None
        self._is_active = stdscr is not None

    def initialize(self) -> None:
        if self._is_active:
            return

        os.environ.setdefault("ESCDELAY", "25")
        self._stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self._stdscr.keypad(True)

        try:
            curses.set_escdelay(25)
        except (AttributeError, curses.error):
            pass

        try:
            curses.start_color()
            curses.use_default_colors()
        except curses.error:
            pass

        self.set_cursor_visibility(True)
        self._is_active = True

    def shutdown(self) -> None:
        if not self._is_active or not self._owns_screen:
            return

        if self._stdscr:
            try:
                self._stdscr.keypad(False)
            except curses.error:
                pass

        try:
            curses.nocbreak()
            curses.echo()
            curses.endwin()
        except curses.error:
            pass

        self._stdscr = None
        self._is_active = False

    def __enter__(self) -> "CursesAdapter":
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.shutdown()

    def get_size(self) -> Tuple[int, int]:
        if not self._stdscr:
            return 24, 80
        max_y, max_x = self._stdscr.getmaxyx()
        return max_y, max_x

    def move_cursor(self, row: int, col: int) -> None:
        if not self._stdscr:
            return
        max_y, max_x = self.get_size()
        r = max(0, min(row, max_y - 1))
        c = max(0, min(col, max_x - 1))
        try:
            self._stdscr.move(r, c)
        except curses.error:
            pass

    def set_cursor_visibility(self, visible: bool) -> None:
        try:
            curses.curs_set(1 if visible else 0)
        except curses.error:
            pass

    def add_str(self, row: int, col: int, text: str, attr: int = 0) -> None:
        if not self._stdscr:
            return

        max_y, max_x = self.get_size()
        if row < 0 or row >= max_y or col < 0 or col >= max_x:
            return

        available_width = max_x - col
        rendered_text = text[:available_width]

        try:
            self._stdscr.addstr(row, col, rendered_text, attr)
        except curses.error:
            pass

    def clear_line(self, row: int) -> None:
        if not self._stdscr:
            return
        max_y, _ = self.get_size()
        if 0 <= row < max_y:
            try:
                self._stdscr.move(row, 0)
                self._stdscr.clrtoeol()
            except curses.error:
                pass

    def clear(self) -> None:
        if self._stdscr:
            self._stdscr.clear()

    def refresh(self) -> None:
        if self._stdscr:
            self._stdscr.refresh()

    def get_key(self) -> int:
        if not self._stdscr:
            return -1

        try:
            ch = self._stdscr.getch()
        except KeyboardInterrupt:
            return 3

        mapping = {
            curses.KEY_UP: KeyCode.UP,
            curses.KEY_DOWN: KeyCode.DOWN,
            curses.KEY_LEFT: KeyCode.LEFT,
            curses.KEY_RIGHT: KeyCode.RIGHT,
            curses.KEY_PPAGE: KeyCode.PAGE_UP,
            curses.KEY_NPAGE: KeyCode.PAGE_DOWN,
            curses.KEY_HOME: KeyCode.HOME,
            curses.KEY_END: KeyCode.END,
            curses.KEY_DC: KeyCode.DELETE,
            curses.KEY_BACKSPACE: KeyCode.KEY_BACKSPACE,
            127: KeyCode.KEY_BACKSPACE,
            8: KeyCode.KEY_BACKSPACE,
            10: KeyCode.ENTER,
            13: KeyCode.ENTER,
            curses.KEY_ENTER: KeyCode.ENTER,
            343: KeyCode.ENTER,
            27: KeyCode.ESC,
        }

        return mapping.get(ch, ch)
