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
        "pass", "lambda", "yield", "and", "or", "not", "is",
        "async", "await", "raise", "global", "nonlocal", "break", "continue",
        "del", "assert"
    }
    _CPP_KEYWORDS = {
        "int", "void", "char", "bool", "auto", "const", "class", "struct",
        "public", "private", "protected", "template", "typename", "new", "delete",
        "include", "namespace", "using", "std", "constexpr", "virtual",
        "override", "static"
    }
    _KEYWORDS = _PYTHON_KEYWORDS | _CPP_KEYWORDS
    _BOOLEAN_LITERALS = {"True", "False", "None", "true", "false", "nullptr"}
    _SELF_WORDS = {"self", "cls", "this"}

    _BUILTINS = {
        "print", "len", "range", "str", "int", "list", "dict", "set", "tuple",
        "open", "type", "isinstance", "super", "enumerate", "zip", "map", "filter",
        "min", "max", "sum", "abs", "hasattr", "getattr", "setattr", "all", "any", "repr"
    }

    _TOKEN_REGEX = re.compile(
        r"(?P<COMMENT>#.*|//.*)|"
        r"(?P<STRING>[frbFRB]?\"\"\"[\s\S]*?\"\"\"|[frbFRB]?\'\'\'[\s\S]*?\'\'\'|[frbFRB]?\"(?:\\.|[^\"\\])*\"|[frbFRB]?\'(?:\\.|[^\'\\])*\')|"
        r"(?P<DECORATOR>@[A-Za-z_][A-Za-z0-9_.]*)|"
        r"(?P<NUMBER>\b0[xXoObB][0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|"
        r"(?P<WORD>\b[A-Za-z_][A-Za-z0-9_]*\b)|"
        r"(?P<OTHER>[^A-Za-z0-9_#\"\'/@]+|.)"
    )

    def __init__(self, target: IEditorView):
        super().__init__(target)
        self._init_colors()

    @classmethod
    def _init_colors(cls) -> None:
        try:
            if hasattr(curses, "has_colors") and curses.has_colors():
                try:
                    curses.use_default_colors()
                    bg = -1
                except (AttributeError, curses.error):
                    bg = getattr(curses, "COLOR_BLACK", 0)

                try:
                    can_256 = getattr(curses, "COLORS", 8) >= 256
                except Exception:
                    can_256 = False

                if can_256:
                    curses.init_pair(1, 208, bg)
                    curses.init_pair(2, 107, bg)
                    curses.init_pair(3, 244, bg)
                    curses.init_pair(4, 68, bg)
                    curses.init_pair(5, 81, bg)
                    curses.init_pair(6, 176, bg)
                    curses.init_pair(7, 221, bg)
                    curses.init_pair(8, 178, bg)
                else:
                    curses.init_pair(1, getattr(curses, "COLOR_YELLOW", 3), bg)
                    curses.init_pair(2, getattr(curses, "COLOR_GREEN", 2), bg)
                    curses.init_pair(3, getattr(curses, "COLOR_WHITE", 7), bg)
                    curses.init_pair(4, getattr(curses, "COLOR_CYAN", 6), bg)
                    curses.init_pair(5, getattr(curses, "COLOR_BLUE", 4), bg)
                    curses.init_pair(6, getattr(curses, "COLOR_MAGENTA", 5), bg)
                    curses.init_pair(7, getattr(curses, "COLOR_YELLOW", 3), bg)
                    curses.init_pair(8, getattr(curses, "COLOR_YELLOW", 3), bg)
        except Exception:
            pass

    def is_syntax_enabled(self) -> bool:
        return True

    def _tokenize(self, text: str) -> List[Tuple[str, str]]:
        tokens = []
        prev_word = None
        for match in self._TOKEN_REGEX.finditer(text):
            kind = match.lastgroup or "OTHER"
            val = match.group()
            if kind == "WORD":
                if val in self._BOOLEAN_LITERALS:
                    kind = "CONSTANT"
                elif val in self._KEYWORDS:
                    kind = "KEYWORD"
                elif val in self._SELF_WORDS:
                    kind = "SELF"
                elif val in self._BUILTINS:
                    kind = "BUILTIN"
                elif prev_word in ("def", "class"):
                    kind = "FUNCTION"
                prev_word = val
            elif kind != "OTHER" or val.strip():
                if val.strip():
                    prev_word = None
            tokens.append((val, kind))
        return tokens

    def _get_attr(self, kind: str) -> int:
        can_colors = False
        can_256 = False
        try:
            if hasattr(curses, "has_colors") and curses.has_colors():
                can_colors = True
                can_256 = getattr(curses, "COLORS", 8) >= 256
        except Exception:
            pass

        can_pair = hasattr(curses, "color_pair")
        bold = getattr(curses, "A_BOLD", 0)
        dim = getattr(curses, "A_DIM", 0)
        underline = getattr(curses, "A_UNDERLINE", 0)

        if can_colors and can_pair:
            try:
                if kind == "KEYWORD":
                    return curses.color_pair(1) | (0 if can_256 else bold)
                elif kind == "CONSTANT":
                    return curses.color_pair(4) | (0 if can_256 else bold)
                elif kind == "STRING":
                    return curses.color_pair(2)
                elif kind == "COMMENT":
                    return curses.color_pair(3) | (0 if can_256 else dim)
                elif kind == "NUMBER":
                    return curses.color_pair(4)
                elif kind == "BUILTIN":
                    return curses.color_pair(5) | (0 if can_256 else bold)
                elif kind == "SELF":
                    return curses.color_pair(6) | bold
                elif kind == "FUNCTION":
                    return curses.color_pair(7) | bold
                elif kind == "DECORATOR":
                    return curses.color_pair(8)
            except Exception:
                pass

        if kind == "KEYWORD":
            return bold
        elif kind == "CONSTANT":
            return bold
        elif kind == "STRING":
            return underline
        elif kind == "COMMENT":
            return dim
        elif kind == "NUMBER":
            return bold
        elif kind == "BUILTIN":
            return bold
        elif kind == "SELF":
            return bold
        elif kind == "FUNCTION":
            return bold
        elif kind == "DECORATOR":
            return 0
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
