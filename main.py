import os
import sys

os.environ.setdefault("ESCDELAY", "25")

from src.adapter.curses_adapter import CursesAdapter
from src.controller.editor_controller import EditorController
from src.model.document import TextDocument
from src.view.editor_view import EditorView


def main() -> None:
    filepath = sys.argv[1] if len(sys.argv) > 1 else None

    doc = TextDocument()
    if filepath:
        if os.path.exists(filepath):
            doc.load(filepath)
        else:
            doc.set_filename(filepath)

    adapter = CursesAdapter()
    view = EditorView(adapter)
    controller = EditorController(doc, adapter, view)

    controller.run()


if __name__ == "__main__":
    main()

