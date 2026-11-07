from enum import Enum
from typing import Optional

from src.adapter.base import ITuiAdapter, KeyCode
from src.model.document import TextDocument
from src.view.editor_view import EditorView


class EditorMode(str, Enum):
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    COMMAND = "COMMAND"
    SEARCH = "SEARCH"


class EditorController:
    def __init__(
        self,
        doc: Optional[TextDocument] = None,
        adapter: Optional[ITuiAdapter] = None,
        view: Optional[EditorView] = None,
    ):
        self._doc = doc if doc is not None else TextDocument()
        self._adapter = adapter
        self._view = view if view is not None else (EditorView(adapter) if adapter else None)
        self._mode = EditorMode.NORMAL
        self._status_message = ""
        self._command_buffer = ""
        self._pending_keys = ""
        self._replace_mode = False
        self._running = False

    def get_document(self) -> TextDocument:
        return self._doc

    def get_view(self) -> Optional[EditorView]:
        return self._view

    def get_adapter(self) -> Optional[ITuiAdapter]:
        return self._adapter

    def get_mode(self) -> EditorMode:
        return self._mode

    def set_mode(self, mode: EditorMode) -> None:
        self._mode = mode
        self._command_buffer = ""
        self._pending_keys = ""

    def get_status_message(self) -> str:
        return self._status_message

    def set_status_message(self, message: str) -> None:
        self._status_message = message

    def is_running(self) -> bool:
        return self._running

    def stop(self) -> None:
        self._running = False

    def handle_key(self, key: int) -> bool:
        if key == -1:
            return True

        if self._mode == EditorMode.NORMAL:
            return self._handle_normal_mode_key(key)
        elif self._mode == EditorMode.INSERT:
            return self._handle_insert_mode_key(key)
        elif self._mode == EditorMode.COMMAND:
            return self._handle_command_mode_key(key)
        elif self._mode == EditorMode.SEARCH:
            return self._handle_search_mode_key(key)

        return True

    def _handle_normal_mode_key(self, key: int) -> bool:
        if self._replace_mode:
            self._replace_mode = False
            if 32 <= key <= 126 or (key > 127 and key < 65536):
                self._doc.replace_char(chr(key))
            return True

        if key in (KeyCode.ESC, 27):
            if self._pending_keys == "ESC":
                self.stop()
                return False
            self._pending_keys = "ESC"
            self._status_message = "Press ESC again to exit, or type :q"
            return True

        if self._pending_keys == "ESC":
            self._pending_keys = ""
            self._status_message = ""

        if key in (ord("q"), 1081) and not self._pending_keys:
            if not self._doc.is_modified():
                self.stop()
                return False
            self._status_message = "No write since last change (use :q! to override)"
            return True

        if key == ord(":"):
            self._mode = EditorMode.COMMAND
            self._command_buffer = ":"
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("/"):
            self._mode = EditorMode.SEARCH
            self._command_buffer = "/"
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("?"):
            self._mode = EditorMode.SEARCH
            self._command_buffer = "?"
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("i"):
            if self._pending_keys == "d":
                self._pending_keys = "di"
                return True
            self._mode = EditorMode.INSERT
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("I"):
            self._doc.move_cursor_line_start()
            self._mode = EditorMode.INSERT
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("A"):
            self._doc.move_cursor_line_end()
            self._doc.move_cursor_right(allow_past_end=True)
            self._mode = EditorMode.INSERT
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("o"):
            self._doc.open_line_below()
            self._mode = EditorMode.INSERT
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("O"):
            self._doc.open_line_above()
            self._mode = EditorMode.INSERT
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("S"):
            self._doc.clear_current_line()
            self._mode = EditorMode.INSERT
            self._status_message = ""
            self._pending_keys = ""
            return True

        if key == ord("r"):
            self._replace_mode = True
            return True

        if key == ord("x") or key == KeyCode.DELETE:
            self._doc.delete_char()
            self._pending_keys = ""
            return True

        if key == ord("p"):
            self._doc.paste()
            self._pending_keys = ""
            return True

        if key == ord("u"):
            if not self._doc.undo():
                self._status_message = "Already at oldest change"
            else:
                self._status_message = "Change undone"
            self._pending_keys = ""
            return True

        if key == ord("U"):
            if not self._doc.undo_line():
                self._status_message = "Line not modified"
            else:
                self._status_message = "Line restored"
            self._pending_keys = ""
            return True

        if key == ord("n"):
            if not self._doc.repeat_search(reverse=False):
                self._status_message = "Pattern not found"
            return True

        if key == ord("N"):
            if not self._doc.repeat_search(reverse=True):
                self._status_message = "Pattern not found"
            return True

        if key in (KeyCode.LEFT, ord("h")):
            self._doc.move_cursor_left()
            self._pending_keys = ""
            return True

        if key in (KeyCode.RIGHT, ord("l")):
            self._doc.move_cursor_right()
            self._pending_keys = ""
            return True

        if key in (KeyCode.UP, ord("k")):
            self._doc.move_cursor_up()
            self._pending_keys = ""
            return True

        if key in (KeyCode.DOWN, ord("j")):
            self._doc.move_cursor_down()
            self._pending_keys = ""
            return True

        if key in (ord("0"), ord("^"), KeyCode.HOME):
            self._doc.move_cursor_line_start()
            self._pending_keys = ""
            return True

        if key in (ord("$"), KeyCode.END):
            self._doc.move_cursor_line_end()
            self._pending_keys = ""
            return True

        if key == KeyCode.PAGE_UP:
            self._doc.page_up()
            self._pending_keys = ""
            return True

        if key == KeyCode.PAGE_DOWN:
            self._doc.page_down()
            self._pending_keys = ""
            return True


        return True

    def _handle_insert_mode_key(self, key: int) -> bool:
        if key in (KeyCode.ESC, 27):
            self._mode = EditorMode.NORMAL
            self._doc.move_cursor_left()
            self._status_message = ""
            return True

        if key in (KeyCode.ENTER, KeyCode.RETURN, 10, 13, 343):
            self._doc.split_line()
            return True

        if key in (KeyCode.KEY_BACKSPACE, KeyCode.BACKSPACE, 8, 127):
            self._doc.backspace()
            return True

        if key == KeyCode.LEFT:
            self._doc.move_cursor_left()
            return True

        if key == KeyCode.RIGHT:
            self._doc.move_cursor_right(allow_past_end=True)
            return True

        if key == KeyCode.UP:
            self._doc.move_cursor_up()
            return True

        if key == KeyCode.DOWN:
            self._doc.move_cursor_down()
            return True

        if 32 <= key <= 126 or (key > 127 and key < 65536):
            self._doc.insert_text(chr(key))
            return True

        return True



    def _handle_command_mode_key(self, key: int) -> bool:
        if key in (KeyCode.ESC, 27):
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            return True

        if key in (KeyCode.ENTER, KeyCode.RETURN):
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            return True

        return True

    def _handle_search_mode_key(self, key: int) -> bool:
        if key in (KeyCode.ESC, 27):
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            return True

        if key in (KeyCode.ENTER, KeyCode.RETURN):
            self._mode = EditorMode.NORMAL
            self._command_buffer = ""
            return True

        return True
