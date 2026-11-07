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
        if key == ord(":"):
            self._mode = EditorMode.COMMAND
            self._command_buffer = ":"
            self._status_message = ""
            return True

        if key == ord("/"):
            self._mode = EditorMode.SEARCH
            self._command_buffer = "/"
            self._status_message = ""
            return True

        if key == ord("?"):
            self._mode = EditorMode.SEARCH
            self._command_buffer = "?"
            self._status_message = ""
            return True

        if key in (ord("i"), ord("I"), ord("A"), ord("o"), ord("S")):
            self._mode = EditorMode.INSERT
            self._status_message = ""
            return True

        if key in (KeyCode.ESC, 27):
            self._pending_keys = ""
            self._status_message = ""
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
