import pytest
from src.adapter.base import KeyCode
from src.adapter.mock_adapter import MockTuiAdapter
from src.controller.editor_controller import EditorController, EditorMode
from src.model.document import TextDocument
from src.view.editor_view import EditorView


def test_controller_initial_state():
    doc = TextDocument("initial text")
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    assert ctrl.get_mode() == EditorMode.NORMAL
    assert not ctrl.is_running()
    assert ctrl.get_status_message() == ""


def test_controller_normal_navigation():
    doc = TextDocument("line 1\nline 2\nline 3")
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    ctrl.handle_key(ord("j"))
    assert doc.get_cursor() == (1, 0)
    ctrl.handle_key(ord("l"))
    assert doc.get_cursor() == (1, 1)
    ctrl.handle_key(ord("k"))
    assert doc.get_cursor() == (0, 1)
    ctrl.handle_key(ord("h"))
    assert doc.get_cursor() == (0, 0)
    ctrl.handle_key(ord("$"))
    assert doc.get_cursor() == (0, 5)
    ctrl.handle_key(ord("0"))
    assert doc.get_cursor() == (0, 0)


def test_controller_multi_key_navigation():
    text = "\n".join([f"line {i}" for i in range(1, 11)])
    doc = TextDocument(text)
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    ctrl.handle_key(ord("G"))
    assert doc.get_cursor() == (9, 0)
    ctrl.handle_key(ord("g"))
    ctrl.handle_key(ord("g"))
    assert doc.get_cursor() == (0, 0)
    ctrl.handle_key(ord("5"))
    ctrl.handle_key(ord("G"))
    assert doc.get_cursor() == (4, 0)


def test_controller_multi_key_editing():
    doc = TextDocument("first line\nsecond line\nthird line")
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    ctrl.handle_key(ord("d"))
    ctrl.handle_key(ord("d"))
    assert doc.get_text() == "second line\nthird line"
    assert doc.get_clipboard() == "first line"
    ctrl.handle_key(ord("p"))
    assert doc.get_text() == "second line\nfirst line\nthird line"

    ctrl.handle_key(ord("y"))
    ctrl.handle_key(ord("y"))
    assert doc.get_clipboard() == "first line"

    doc.set_text("word1 word2 word3")
    doc.set_cursor(0, 7)
    ctrl.handle_key(ord("d"))
    ctrl.handle_key(ord("i"))
    ctrl.handle_key(ord("w"))
    assert doc.get_text() == "word1 word3"

    doc.set_cursor(0, 0)
    ctrl.handle_key(ord("y"))
    ctrl.handle_key(ord("w"))
    assert doc.get_clipboard() == "word1 "


def test_controller_insert_mode():
    doc = TextDocument("ac")
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    doc.set_cursor(0, 1)
    ctrl.handle_key(ord("i"))
    assert ctrl.get_mode() == EditorMode.INSERT
    ctrl.handle_key(ord("b"))
    assert doc.get_line(0).c_str() == "abc"
    ctrl.handle_key(KeyCode.ENTER)
    assert doc.get_line_count() == 2
    ctrl.handle_key(KeyCode.BACKSPACE)
    assert doc.get_line_count() == 1
    ctrl.handle_key(KeyCode.ESC)
    assert ctrl.get_mode() == EditorMode.NORMAL


def test_controller_insert_mode_shortcuts():
    doc = TextDocument("hello")
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    ctrl.handle_key(ord("A"))
    assert ctrl.get_mode() == EditorMode.INSERT
    assert doc.get_cursor() == (0, 5)
    ctrl.handle_key(KeyCode.ESC)

    ctrl.handle_key(ord("I"))
    assert ctrl.get_mode() == EditorMode.INSERT
    assert doc.get_cursor() == (0, 0)
    ctrl.handle_key(KeyCode.ESC)

    ctrl.handle_key(ord("o"))
    assert ctrl.get_mode() == EditorMode.INSERT
    assert doc.get_line_count() == 2
    assert doc.get_cursor() == (1, 0)
    ctrl.handle_key(KeyCode.ESC)

    ctrl.handle_key(ord("S"))
    assert ctrl.get_mode() == EditorMode.INSERT
    assert doc.get_line(1).c_str() == ""
    ctrl.handle_key(KeyCode.ESC)


def test_controller_replace_char():
    doc = TextDocument("hello")
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    doc.set_cursor(0, 1)
    ctrl.handle_key(ord("r"))
    ctrl.handle_key(ord("a"))
    assert doc.get_line(0).c_str() == "hallo"
    assert ctrl.get_mode() == EditorMode.NORMAL


def test_controller_command_save_and_exit(tmp_path):
    fpath = tmp_path / "test.txt"
    doc = TextDocument("content to save")
    doc.set_filename(str(fpath))
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    for ch in ":w":
        ctrl.handle_key(ord(ch))
    ctrl.handle_key(KeyCode.ENTER)
    assert fpath.read_text(encoding="utf-8") == "content to save"

    for ch in ":q":
        ctrl.handle_key(ord(ch))
    res = ctrl.handle_key(KeyCode.ENTER)
    assert not res
    assert not ctrl.is_running()


def test_controller_command_modified_exit():
    doc = TextDocument("fresh content")
    doc.set_cursor(0, 0)
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    ctrl.handle_key(ord("i"))
    ctrl.handle_key(ord("X"))
    ctrl.handle_key(KeyCode.ESC)
    assert doc.is_modified()

    for ch in ":q":
        ctrl.handle_key(ord(ch))
    res = ctrl.handle_key(KeyCode.ENTER)
    assert res
    assert "No write since last change" in ctrl.get_status_message()

    for ch in ":q!":
        ctrl.handle_key(ord(ch))
    res2 = ctrl.handle_key(KeyCode.ENTER)
    assert not res2
    assert not ctrl.is_running()


def test_controller_command_open_and_revert(tmp_path):
    fpath = tmp_path / "sample.txt"
    fpath.write_text("file body", encoding="utf-8")
    doc = TextDocument()
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    for ch in f":o {fpath}":
        ctrl.handle_key(ord(ch))
    ctrl.handle_key(KeyCode.ENTER)
    assert doc.get_text() == "file body"

    ctrl.handle_key(ord("i"))
    ctrl.handle_key(ord("!"))
    ctrl.handle_key(KeyCode.ESC)
    assert doc.is_modified()

    for ch in ":e!":
        ctrl.handle_key(ord(ch))
    ctrl.handle_key(KeyCode.ENTER)
    assert doc.get_text() == "file body"
    assert not doc.is_modified()


def test_controller_search_mode():
    doc = TextDocument("alpha beta gamma beta delta")
    adapter = MockTuiAdapter()
    ctrl = EditorController(doc, adapter)
    for ch in "/beta":
        ctrl.handle_key(ord(ch))
    ctrl.handle_key(KeyCode.ENTER)
    assert doc.get_cursor() == (0, 6)

    ctrl.handle_key(ord("n"))
    assert doc.get_cursor() == (0, 17)
    ctrl.handle_key(ord("N"))
    assert doc.get_cursor() == (0, 6)


def test_controller_run_loop_simulation():
    doc = TextDocument("line 1\nline 2")
    adapter = MockTuiAdapter()
    adapter.feed_input([ord("j"), ord("x"), ord(":"), ord("q"), ord("!"), KeyCode.ENTER])
    view = EditorView(adapter)
    ctrl = EditorController(doc, adapter, view)
    ctrl.run()
    assert not ctrl.is_running()
    assert doc.get_cursor() == (1, 0)

