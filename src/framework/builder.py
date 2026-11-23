from abc import ABC, abstractmethod
from typing import Any, Optional, List
from src.adapter.base import ITuiAdapter
from src.framework.application import TuiApplication


class IApplicationBuilder(ABC):
    @abstractmethod
    def set_adapter(self, adapter: ITuiAdapter) -> "IApplicationBuilder":
        pass

    @abstractmethod
    def set_model(self, model: Any) -> "IApplicationBuilder":
        pass

    @abstractmethod
    def set_view(self, view: Any) -> "IApplicationBuilder":
        pass

    @abstractmethod
    def add_view(self, view: Any) -> "IApplicationBuilder":
        pass

    @abstractmethod
    def set_views(self, views: List[Any]) -> "IApplicationBuilder":
        pass

    @abstractmethod
    def set_controller(self, controller: Any) -> "IApplicationBuilder":
        pass

    @abstractmethod
    def build(self) -> TuiApplication:
        pass


class ApplicationBuilder(IApplicationBuilder):
    def __init__(self) -> None:
        self._adapter: Optional[ITuiAdapter] = None
        self._model: Optional[Any] = None
        self._views: List[Any] = []
        self._controller: Optional[Any] = None

    def reset(self) -> "ApplicationBuilder":
        self._adapter = None
        self._model = None
        self._views = []
        self._controller = None
        return self

    def set_adapter(self, adapter: ITuiAdapter) -> "ApplicationBuilder":
        self._adapter = adapter
        return self

    def set_model(self, model: Any) -> "ApplicationBuilder":
        self._model = model
        return self

    def set_view(self, view: Any) -> "ApplicationBuilder":
        self._views = [view] if view is not None else []
        return self

    def add_view(self, view: Any) -> "ApplicationBuilder":
        if view is not None:
            self._views.append(view)
        return self

    def set_views(self, views: List[Any]) -> "ApplicationBuilder":
        self._views = list(views) if views else []
        return self

    def set_controller(self, controller: Any) -> "ApplicationBuilder":
        self._controller = controller
        return self

    def build(self) -> TuiApplication:
        if self._adapter is None:
            raise ValueError("Adapter must be set before building application")
        if self._model is None:
            raise ValueError("Model must be set before building application")
        if not self._views:
            raise ValueError("View must be set before building application")
        if self._controller is None:
            raise ValueError("Controller must be set before building application")

        app = TuiApplication(
            adapter=self._adapter,
            model=self._model,
            view=self._views[0],
            controller=self._controller,
            views=self._views,
        )
        return app


class ApplicationDirector:
    def __init__(self, builder: Optional[IApplicationBuilder] = None):
        self._builder = builder if builder is not None else ApplicationBuilder()

    def set_builder(self, builder: IApplicationBuilder) -> None:
        self._builder = builder

    def construct(
        self,
        adapter: ITuiAdapter,
        model: Any,
        view: Any,
        controller: Any,
        extra_views: Optional[List[Any]] = None,
    ) -> TuiApplication:
        builder = (
            self._builder
            .set_adapter(adapter)
            .set_model(model)
            .set_view(view)
            .set_controller(controller)
        )
        if extra_views:
            for ev in extra_views:
                builder.add_view(ev)
        return builder.build()
