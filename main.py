import os
import sys
from typing import Optional

os.environ.setdefault("ESCDELAY", "25")

from src.adapter.curses_adapter import CursesAdapter
from src.controller.editor_controller import EditorController
from src.model.document import TextDocument
from src.view.editor_view import EditorView


class EditorApplication:
    def __init__(self, filepath: Optional[str] = None):
        self.doc = TextDocument()
        if filepath:
            if os.path.exists(filepath):
                self.doc.load(filepath)
            else:
                self.doc.set_filename(filepath)

        self.adapter = CursesAdapter()
        self.view = EditorView(self.adapter)
        self.controller = EditorController(self.doc, self.adapter, self.view)

    def create_editor(self) -> EditorController:
        return self.controller

    def run(self) -> None:
        self.controller.run()

    @classmethod
    def main(cls) -> None:
        filepath = sys.argv[1] if len(sys.argv) > 1 else None
        app = cls(filepath)
        app.run()


def main() -> None:
    EditorApplication.main()


if __name__ == "__main__":
    main()
