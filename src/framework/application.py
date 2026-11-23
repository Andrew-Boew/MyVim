from typing import Any, List, Optional
from src.adapter.base import ITuiAdapter
from src.framework.base import ITuiApplication


class TuiApplication(ITuiApplication):
    def __init__(
        self,
        adapter: ITuiAdapter,
        model: Any,
        view: Any,
        controller: Any,
        views: Optional[List[Any]] = None,
    ):
        self._adapter = adapter
        self._model = model
        if views is not None:
            self._views = list(views)
        elif isinstance(view, (list, tuple)):
            self._views = list(view)
        elif view is not None:
            self._views = [view]
        else:
            self._views = []
        self._view = self._views[0] if self._views else None
        self._controller = controller

    def get_adapter(self) -> ITuiAdapter:
        return self._adapter

    def get_model(self) -> Any:
        return self._model

    def get_view(self) -> Any:
        return self._view

    def get_views(self) -> List[Any]:
        return self._views

    def add_view(self, view: Any) -> None:
        if view is not None:
            self._views.append(view)
            if self._view is None:
                self._view = view

    def get_controller(self) -> Any:
        return self._controller

    def render_views(self) -> None:
        for v in self._views:
            if hasattr(v, "render"):
                v.render()

    def run(self) -> None:
        if hasattr(self._controller, "run"):
            self._controller.run()
            return

        self._adapter.initialize()
        try:
            if hasattr(self._controller, "start"):
                self._controller.start()

            self.render_views()
            if hasattr(self._controller, "render"):
                self._controller.render()

            while getattr(self._controller, "is_running", lambda: True)():
                try:
                    key = self._adapter.get_key()
                except KeyboardInterrupt:
                    break

                if key != -1:
                    if hasattr(self._controller, "handle_key"):
                        if not self._controller.handle_key(key):
                            break

                self.render_views()
                if hasattr(self._controller, "render"):
                    self._controller.render()
        except KeyboardInterrupt:
            pass
        finally:
            self._adapter.shutdown()
