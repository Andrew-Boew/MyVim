import pytest
from src.model.document import TextDocument
from src.model.text_line import TextLine


def test_navigation_left_right():
    doc = TextDocument("hello")
    doc.set_cursor(0, 2)
    doc.move_cursor_left()
    assert doc.get_cursor() == (0, 1)
    doc.move_cursor_left()
    assert doc.get_cursor() == (0, 0)
    doc.move_cursor_left()
    assert doc.get_cursor() == (0, 0)
    doc.move_cursor_right()
    assert doc.get_cursor() == (0, 1)
    doc.move_cursor_right()
    doc.move_cursor_right()
    doc.move_cursor_right()
    assert doc.get_cursor() == (0, 4)
    doc.move_cursor_right()
    assert doc.get_cursor() == (0, 4)


def test_navigation_up_down_desired_col():
    text = "first long line\nhi\nthird long line"
    doc = TextDocument(text)
    doc.set_cursor(0, 10)
    assert doc.get_cursor() == (0, 10)
    doc.move_cursor_down()
    assert doc.get_cursor() == (1, 1)
    doc.move_cursor_down()
    assert doc.get_cursor() == (2, 10)
    doc.move_cursor_up()
    assert doc.get_cursor() == (1, 1)
    doc.move_cursor_up()
    assert doc.get_cursor() == (0, 10)


def test_navigation_line_start_end():
    doc = TextDocument("hello world")
    doc.set_cursor(0, 5)
    doc.move_cursor_line_start()
    assert doc.get_cursor() == (0, 0)
    doc.move_cursor_line_end()
    assert doc.get_cursor() == (0, 10)


def test_navigation_words():
    text = "one two three\nfour five"
    doc = TextDocument(text)
    doc.set_cursor(0, 0)
    doc.move_cursor_word_forward()
    assert doc.get_cursor() == (0, 2)
    doc.move_cursor_word_forward()
    assert doc.get_cursor() == (0, 6)
    doc.move_cursor_word_forward()
    assert doc.get_cursor() == (0, 12)
    doc.move_cursor_word_forward()
    assert doc.get_cursor() == (1, 3)
    doc.move_cursor_word_backward()
    assert doc.get_cursor() == (1, 0)
    doc.move_cursor_word_backward()
    assert doc.get_cursor() == (0, 8)


def test_navigation_file_start_end_line():
    text = "line1\nline2\nline3\nline4\nline5"
    doc = TextDocument(text)
    doc.set_cursor(2, 2)
    doc.move_cursor_file_start()
    assert doc.get_cursor() == (0, 0)
    doc.move_cursor_file_end()
    assert doc.get_cursor() == (4, 0)
    doc.move_cursor_to_line(3)
    assert doc.get_cursor() == (2, 0)
    doc.move_cursor_to_line(100)
    assert doc.get_cursor() == (4, 0)
    doc.move_cursor_to_line(0)
    assert doc.get_cursor() == (0, 0)


def test_navigation_page_up_down():
    lines = [f"line {i}" for i in range(50)]
    doc = TextDocument("\n".join(lines))
    assert doc.get_cursor() == (0, 0)
    doc.page_down(20)
    assert doc.get_cursor()[0] == 20
    doc.page_down(20)
    assert doc.get_cursor()[0] == 40
    doc.page_down(20)
    assert doc.get_cursor()[0] == 49
    doc.page_up(25)
    assert doc.get_cursor()[0] == 24
    doc.page_up(50)
    assert doc.get_cursor()[0] == 0


def test_edit_delete_char():
    doc = TextDocument("abcdef")
    doc.set_cursor(0, 2)
    doc.delete_char()
    assert doc.get_line(0).c_str() == "abdef"
    assert doc.get_clipboard() == "c"
    assert not doc.is_clipboard_line()
    assert doc.is_modified()


def test_edit_delete_word():
    doc = TextDocument("alpha beta gamma")
    doc.set_cursor(0, 6)
    doc.delete_word()
    assert doc.get_line(0).c_str() == "alpha gamma"
    assert doc.get_clipboard() == "beta "
    assert not doc.is_clipboard_line()
    assert doc.is_modified()


def test_edit_cut_and_paste_line():
    text = "first\nsecond\nthird"
    doc = TextDocument(text)
    doc.set_cursor(1, 0)
    doc.cut_line()
    assert doc.get_text() == "first\nthird"
    assert doc.get_clipboard() == "second"
    assert doc.is_clipboard_line()
    doc.set_cursor(0, 0)
    doc.paste()
    assert doc.get_text() == "first\nsecond\nthird"
    assert doc.get_cursor() == (1, 0)


def test_edit_copy_and_paste_word():
    doc = TextDocument("cat dog")
    doc.set_cursor(0, 0)
    doc.copy_word()
    assert doc.get_clipboard() == "cat "
    assert not doc.is_clipboard_line()
    doc.set_cursor(0, 6)
    doc.paste()
    assert doc.get_line(0).c_str() == "cat dogcat "


def test_edit_copy_line():
    doc = TextDocument("single line")
    doc.copy_line()
    assert doc.get_clipboard() == "single line"
    assert doc.is_clipboard_line()


def test_edit_replace_char():
    doc = TextDocument("hello")
    doc.set_cursor(0, 1)
    doc.replace_char("a")
    assert doc.get_line(0).c_str() == "hallo"
    assert doc.is_modified()


def test_edit_clear_current_line():
    doc = TextDocument("something to clear")
    doc.clear_current_line()
    assert doc.get_line(0).c_str() == ""
    assert doc.get_cursor() == (0, 0)
    assert doc.is_modified()


def test_edit_insert_and_split_and_backspace():
    doc = TextDocument("ac")
    doc.set_cursor(0, 1)
    doc.insert_text("b")
    assert doc.get_line(0).c_str() == "abc"
    assert doc.get_cursor() == (0, 2)
    doc.split_line()
    assert doc.get_line_count() == 2
    assert doc.get_line(0).c_str() == "ab"
    assert doc.get_line(1).c_str() == "c"
    assert doc.get_cursor() == (1, 0)
    doc.backspace()
    assert doc.get_line_count() == 1
    assert doc.get_line(0).c_str() == "abc"
    assert doc.get_cursor() == (0, 2)
    doc.backspace()
    assert doc.get_line(0).c_str() == "ac"
    assert doc.get_cursor() == (0, 1)


def test_undo_and_undo_line():
    doc = TextDocument("original line")
    doc.set_cursor(0, 0)
    doc.insert_text("X")
    assert doc.get_line(0).c_str() == "Xoriginal line"
    doc.insert_text("Y")
    assert doc.get_line(0).c_str() == "XYoriginal line"
    doc.undo()
    assert doc.get_line(0).c_str() == "Xoriginal line"
    doc.undo()
    assert doc.get_line(0).c_str() == "original line"
    doc.insert_text("1")
    doc.insert_text("2")
    doc.undo_line()
    assert doc.get_line(0).c_str() == "original line"


def test_revert(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("file content", encoding="utf-8")
    doc = TextDocument()
    doc.load(str(file_path))
    assert doc.get_text() == "file content"
    doc.insert_text("modified ")
    assert doc.is_modified()
    doc.revert()
    assert doc.get_text() == "file content"
    assert not doc.is_modified()


def test_search_forward_and_repeat():
    text = "apple banana cherry banana date"
    doc = TextDocument(text)
    assert doc.search("banana", forward=True)
    assert doc.get_cursor() == (0, 6)
    assert doc.repeat_search(reverse=False)
    assert doc.get_cursor() == (0, 20)
    assert doc.repeat_search(reverse=False)
    assert doc.get_cursor() == (0, 6)


def test_search_backward_and_repeat():
    text = "first target middle target last"
    doc = TextDocument(text)
    doc.set_cursor(0, 27)
    assert doc.search("target", forward=False)
    assert doc.get_cursor() == (0, 20)
    assert doc.repeat_search(reverse=False)
    assert doc.get_cursor() == (0, 6)
    assert doc.repeat_search(reverse=True)
    assert doc.get_cursor() == (0, 20)


def test_search_not_found():
    doc = TextDocument("hello world")
    assert not doc.search("python")
    assert not doc.repeat_search()
