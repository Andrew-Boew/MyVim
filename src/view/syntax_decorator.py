import curses
import re
from typing import List, Tuple
from src.adapter.base import ITuiAdapter
from src.model.document import TextDocument
from src.view.editor_view import IEditorView


class EditorViewDecorator(IEditorView):
    def __init__(self, target: IEditorView):
        self._target = target

    def get_target(self) -> IEditorView:
        return self._target

    def unwrap(self) -> IEditorView:
        if isinstance(self._target, EditorViewDecorator):
            return self._target.unwrap()
        return self._target

    def toggle_line_numbers(self) -> bool:
        return self._target.toggle_line_numbers()

    def set_line_numbers(self, enabled: bool) -> None:
        self._target.set_line_numbers(enabled)

    def is_line_numbers_enabled(self) -> bool:
        return self._target.is_line_numbers_enabled()

    def get_adapter(self) -> ITuiAdapter:
        return self._target.get_adapter()

    def get_viewport_size(self) -> Tuple[int, int]:
        return self._target.get_viewport_size()

    def is_syntax_enabled(self) -> bool:
        return self._target.is_syntax_enabled()

    def render(
        self,
        doc: TextDocument,
        mode_name: str,
        status_message: str = "",
        command_buffer: str = "",
    ) -> None:
        self._target.render(doc, mode_name, status_message, command_buffer)


class SyntaxHighlightDecorator(EditorViewDecorator):
    _PYTHON_KEYWORDS = {
        "def", "class", "import", "from", "return", "if", "elif", "else",
        "while", "for", "in", "try", "except", "finally", "with", "as",
        "pass", "lambda", "yield", "None", "True", "False", "and", "or", "not", "is"
    }
    _CPP_KEYWORDS = {
        "int", "void", "char", "bool", "auto", "const", "class", "struct",
        "public", "private", "protected", "template", "typename", "new", "delete"
    }
    _KEYWORDS = _PYTHON_KEYWORDS | _CPP_KEYWORDS

    _TOKEN_REGEX = re.compile(
        r"(?P<COMMENT>#.*|//.*)|"
        r"(?P<STRING>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')|"
        r"(?P<NUMBER>\b\d+(?:\.\d+)?\b)|"
        r"(?P<WORD>\b[A-Za-z_][A-Za-z0-9_]*\b)|"
        r"(?P<OTHER>[^A-Za-z0-9_#\"\'/]+|.)"
    )

    def is_syntax_enabled(self) -> bool:
        return True

    def _tokenize(self, text: str) -> List[Tuple[str, str]]:
        tokens = []
        for match in self._TOKEN_REGEX.finditer(text):
            kind = match.lastgroup or "OTHER"
            val = match.group()
            if kind == "WORD" and val in self._KEYWORDS:
                kind = "KEYWORD"
            tokens.append((val, kind))
        return tokens

    def _get_attr(self, kind: str) -> int:
        try:
            if hasattr(curses, "has_colors") and curses.has_colors():
                if kind == "KEYWORD":
                    return curses.color_pair(1) | curses.A_BOLD if hasattr(curses, "color_pair") else curses.A_BOLD
                elif kind == "STRING":
                    return curses.color_pair(2) if hasattr(curses, "color_pair") else curses.A_UNDERLINE
                elif kind == "COMMENT":
                    return curses.color_pair(3) if hasattr(curses, "color_pair") else curses.A_DIM
                elif kind == "NUMBER":
                    return curses.color_pair(4) if hasattr(curses, "color_pair") else curses.A_BOLD
        except Exception:
            pass

        if kind == "KEYWORD":
            return getattr(curses, "A_BOLD", 1)
        elif kind == "STRING":
            return getattr(curses, "A_UNDERLINE", 2)
        elif kind == "COMMENT":
            return getattr(curses, "A_DIM", 3)
        elif kind == "NUMBER":
            return getattr(curses, "A_BOLD", 4)
        return 0

    def render(
        self,
        doc: TextDocument,
        mode_name: str,
        status_message: str = "",
        command_buffer: str = "",
    ) -> None:
        adapter = self.get_adapter()
        height, width = adapter.get_size()
        if height < 3 or width < 10:
            return

        text_height = height - 2
        lines = doc.get_lines()
        total_lines = len(lines)

        is_num = self.is_line_numbers_enabled()
        gutter_digits = max(3, len(str(total_lines)))
        gutter_width = (gutter_digits + 1) if is_num else 0
        avail_width = max(1, width - gutter_width)

        cursor_row, cursor_col = doc.get_cursor()
        target = self.unwrap()
        if hasattr(target, "_adjust_scroll"):
            target._adjust_scroll(cursor_row, cursor_col, text_height, avail_width)
            scroll_row = getattr(target, "_scroll_row", 0)
            scroll_col = getattr(target, "_scroll_col", 0)
        else:
            scroll_row = 0
            scroll_col = 0

        adapter.clear()

        for screen_row in range(text_height):
            file_row = scroll_row + screen_row
            if file_row < total_lines:
                line_content = lines[file_row].c_str()
                if scroll_col < len(line_content):
                    visible_slice = line_content[scroll_col : scroll_col + avail_width]
                else:
                    visible_slice = ""

                if is_num:
                    gutter = str(file_row + 1).rjust(gutter_digits) + " "
                    adapter.add_str(screen_row, 0, gutter, 0)

                col_pos = gutter_width
                tokens = self._tokenize(visible_slice)
                for tok_text, tok_kind in tokens:
                    if col_pos >= width:
                        break
                    tok_attr = self._get_attr(tok_kind)
                    adapter.add_str(screen_row, col_pos, tok_text, tok_attr)
                    col_pos += len(tok_text)
            else:
                gutter = (" " * gutter_width) if is_num else ""
                adapter.add_str(screen_row, 0, gutter + "~", 0)

        status_row = height - 2
        fname = doc.get_filename() or "[No Name]"
        mod_flag = " [+]" if doc.is_modified() else ""
        left_status = f"-- {mode_name} --  {fname}{mod_flag} [syntax]"
        right_status = f"{cursor_row + 1}/{total_lines}"

        space_count = max(1, width - len(left_status) - len(right_status) - 1)
        status_line = left_status + (" " * space_count) + right_status
        adapter.add_str(status_row, 0, status_line[:width])

        bottom_row = height - 1
        if mode_name in ("COMMAND", "SEARCH"):
            adapter.add_str(bottom_row, 0, command_buffer[:width])
        else:
            if status_message:
                adapter.add_str(bottom_row, 0, status_message[:width])

        if mode_name in ("COMMAND", "SEARCH"):
            adapter.move_cursor(bottom_row, min(len(command_buffer), width - 1))
        else:
            screen_cur_row = cursor_row - scroll_row
            screen_cur_col = gutter_width + cursor_col - scroll_col
            adapter.move_cursor(screen_cur_row, screen_cur_col)

        adapter.refresh()
