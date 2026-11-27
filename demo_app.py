import sys
from dataclasses import dataclass
from typing import List, Optional, Any

from src.adapter.base import ITuiAdapter, KeyCode
from src.adapter.curses_adapter import CursesAdapter
from src.framework.application import TuiApplication
from src.framework.base import ITuiController, ITuiModel, ITuiView
from src.framework.builder import ApplicationBuilder


@dataclass
class ProcessItem:
    pid: int
    name: str
    user: str
    cpu_percent: float
    memory_percent: float
    state: str = "RUNNING"


class SystemMonitorModel(ITuiModel):
    def __init__(self) -> None:
        self._sort_key = "cpu"
        self._is_paused = False
        self._processes: List[ProcessItem] = [
            ProcessItem(1, "systemd", "root", 0.2, 0.8, "SLEEPING"),
            ProcessItem(142, "sshd", "root", 0.1, 0.5, "SLEEPING"),
            ProcessItem(256, "cron", "root", 0.0, 0.3, "SLEEPING"),
            ProcessItem(412, "nginx-master", "www-data", 1.4, 2.1, "SLEEPING"),
            ProcessItem(413, "nginx-worker", "www-data", 4.8, 3.4, "RUNNING"),
            ProcessItem(680, "postgres-db", "postgres", 6.2, 14.5, "RUNNING"),
            ProcessItem(820, "redis-server", "redis", 2.1, 4.2, "RUNNING"),
            ProcessItem(1024, "python3-app", "user", 12.8, 8.6, "RUNNING"),
            ProcessItem(1150, "node-worker", "user", 7.5, 6.1, "RUNNING"),
            ProcessItem(1340, "zsh", "user", 0.1, 0.4, "SLEEPING"),
            ProcessItem(1480, "docker-daemon", "root", 3.2, 5.8, "SLEEPING"),
            ProcessItem(1620, "metrics-agent", "user", 1.9, 1.2, "RUNNING"),
        ]

    def get_state(self) -> List[ProcessItem]:
        return self.get_processes()

    def get_processes(self) -> List[ProcessItem]:
        procs = list(self._processes)
        if self._sort_key == "cpu":
            procs.sort(key=lambda p: p.cpu_percent, reverse=True)
        elif self._sort_key == "mem":
            procs.sort(key=lambda p: p.memory_percent, reverse=True)
        elif self._sort_key == "pid":
            procs.sort(key=lambda p: p.pid)
        elif self._sort_key == "name":
            procs.sort(key=lambda p: p.name.lower())
        return procs

    def get_total_cpu(self) -> float:
        return sum(p.cpu_percent for p in self._processes)

    def get_total_memory(self) -> float:
        return sum(p.memory_percent for p in self._processes)

    def get_sort_key(self) -> str:
        return self._sort_key

    def cycle_sort(self) -> str:
        order = ["cpu", "mem", "pid", "name"]
        curr = order.index(self._sort_key) if self._sort_key in order else 0
        self._sort_key = order[(curr + 1) % len(order)]
        return self._sort_key

    def toggle_pause(self) -> bool:
        self._is_paused = not self._is_paused
        return self._is_paused

    def is_paused(self) -> bool:
        return self._is_paused

    def kill_process(self, index: int) -> bool:
        procs = self.get_processes()
        if 0 <= index < len(procs):
            target_pid = procs[index].pid
            self._processes = [p for p in self._processes if p.pid != target_pid]
            return True
        return False

    def spawn_process(self, name: str, user: str = "user") -> Optional[ProcessItem]:
        if not name.strip():
            return None
        new_pid = max((p.pid for p in self._processes), default=1000) + 1
        item = ProcessItem(new_pid, name.strip(), user, 5.0, 2.5, "RUNNING")
        self._processes.append(item)
        return item


class SystemHeaderDashboardView(ITuiView):
    def __init__(self, adapter: ITuiAdapter, model: SystemMonitorModel):
        self._adapter = adapter
        self._model = model

    def _render_bar(self, percent: float, width: int) -> str:
        avail = max(4, width - 8)
        filled = int((min(100.0, percent) / 100.0) * avail)
        empty = avail - filled
        bar = "[" + ("|" * filled) + (" " * empty) + f"] {percent:4.1f}%"
        return bar

    def render(self) -> None:
        height, width = self._adapter.get_size()
        if height < 4 or width < 30:
            return
        title = "=== TUI SYSTEM MONITOR (MVC FRAMEWORK & BUILDER) ==="
        self._adapter.add_str(0, 0, title[:width], 1)
        total_cpu = self._model.get_total_cpu()
        total_mem = self._model.get_total_memory()
        cpu_bar = "CPU " + self._render_bar(total_cpu, min(36, width // 2))
        mem_bar = "MEM " + self._render_bar(total_mem, min(36, width // 2))
        paused_flag = " [PAUSED]" if self._model.is_paused() else ""
        header_stats = f"{cpu_bar}  |  {mem_bar}{paused_flag}"
        self._adapter.add_str(1, 0, header_stats[:width], 0)
        procs = self._model.get_processes()
        running_cnt = sum(1 for p in procs if p.state == "RUNNING")
        info_line = f"Tasks: {len(procs)} total, {running_cnt} running | Sort: {self._model.get_sort_key().upper()}"
        self._adapter.add_str(2, 0, info_line[:width], 0)
        col_header = "  PID     USER         CPU%    MEM%    STATE      COMMAND"
        self._adapter.add_str(3, 0, col_header[:width], 1)


class ProcessTableView(ITuiView):
    def __init__(self, adapter: ITuiAdapter, model: SystemMonitorModel, monitor_view: Optional[Any] = None):
        self._adapter = adapter
        self._model = model
        self._monitor_view = monitor_view

    def render(self) -> None:
        if self._monitor_view is not None:
            self._monitor_view.render()
        else:
            height, width = self._adapter.get_size()
            if height < 8 or width < 30:
                return
            procs = self._model.get_processes()
            table_rows = height - 6
            for i in range(min(len(procs), table_rows)):
                p = procs[i]
                row_str = f"   {p.pid:<6} {p.user:<12} {p.cpu_percent:>5.1f}%  {p.memory_percent:>5.1f}%  {p.state:<10} {p.name}"
                self._adapter.add_str(i + 4, 0, row_str[:width], 0)
            hint = "[s] Sort | [k/d] Kill | [n] Spawn | [Space] Pause | [j/k] Select | [q] Quit"
            self._adapter.add_str(height - 1, 0, hint[:width])


class SystemMonitorView(ITuiView):
    def __init__(self, adapter: ITuiAdapter, model: SystemMonitorModel):
        self._adapter = adapter
        self._model = model

    def _render_bar(self, percent: float, width: int) -> str:
        avail = max(4, width - 8)
        filled = int((min(100.0, percent) / 100.0) * avail)
        empty = avail - filled
        bar = "[" + ("|" * filled) + (" " * empty) + f"] {percent:4.1f}%"
        return bar

    def render_screen(
        self,
        selected_index: int,
        input_buffer: str = "",
        is_input_mode: bool = False,
    ) -> None:
        height, width = self._adapter.get_size()
        if height < 8 or width < 30:
            return

        self._adapter.clear()

        title = "=== TUI SYSTEM MONITOR (MVC FRAMEWORK & BUILDER) ==="
        self._adapter.add_str(0, 0, title[:width], 1)

        total_cpu = self._model.get_total_cpu()
        total_mem = self._model.get_total_memory()

        cpu_bar = "CPU " + self._render_bar(total_cpu, min(36, width // 2))
        mem_bar = "MEM " + self._render_bar(total_mem, min(36, width // 2))

        paused_flag = " [PAUSED]" if self._model.is_paused() else ""
        header_stats = f"{cpu_bar}  |  {mem_bar}{paused_flag}"
        self._adapter.add_str(1, 0, header_stats[:width], 0)

        procs = self._model.get_processes()
        running_cnt = sum(1 for p in procs if p.state == "RUNNING")
        info_line = f"Tasks: {len(procs)} total, {running_cnt} running | Sort: {self._model.get_sort_key().upper()}"
        self._adapter.add_str(2, 0, info_line[:width], 0)

        col_header = "  PID     USER         CPU%    MEM%    STATE      COMMAND"
        self._adapter.add_str(3, 0, col_header[:width], 1)

        table_rows = height - 6
        for i in range(min(len(procs), table_rows)):
            p = procs[i]
            prefix = " >" if i == selected_index else "  "
            row_str = f"{prefix} {p.pid:<6} {p.user:<12} {p.cpu_percent:>5.1f}%  {p.memory_percent:>5.1f}%  {p.state:<10} {p.name}"
            attr = 1 if i == selected_index else 0
            self._adapter.add_str(i + 4, 0, row_str[:width], attr)

        bottom_row = height - 1
        if is_input_mode:
            prompt = f"Spawn process: {input_buffer}"
            self._adapter.add_str(bottom_row, 0, prompt[:width])
            self._adapter.move_cursor(bottom_row, min(len(prompt), width - 1))
        else:
            hint = "[s] Sort | [k/d] Kill | [n] Spawn | [Space] Pause | [j/k] Select | [q] Quit"
            self._adapter.add_str(bottom_row, 0, hint[:width])
            cursor_row = min(selected_index + 4, height - 2)
            self._adapter.move_cursor(cursor_row, 1)

        self._adapter.refresh()

    def render(self) -> None:
        self.render_screen(0)


class SystemMonitorController(ITuiController):
    def __init__(
        self,
        model: SystemMonitorModel,
        view: SystemMonitorView,
        adapter: ITuiAdapter,
    ):
        self._model = model
        self._view = view
        self._adapter = adapter
        self._selected = 0
        self._running = False
        self._input_mode = False
        self._input_buffer = ""

    def start(self) -> None:
        self._running = True

    def is_running(self) -> bool:
        return self._running

    def stop(self) -> None:
        self._running = False

    def render(self) -> None:
        self._view.render_screen(self._selected, self._input_buffer, self._input_mode)

    def handle_key(self, key: int) -> bool:
        if self._input_mode:
            if key in (KeyCode.ENTER, 10, 13):
                if self._input_buffer.strip():
                    self._model.spawn_process(self._input_buffer.strip())
                self._input_buffer = ""
                self._input_mode = False
            elif key in (KeyCode.ESC, 27):
                self._input_buffer = ""
                self._input_mode = False
            elif key in (KeyCode.BACKSPACE, 127, 8):
                if self._input_buffer:
                    self._input_buffer = self._input_buffer[:-1]
            elif 32 <= key <= 126:
                self._input_buffer += chr(key)
            return True

        procs = self._model.get_processes()
        total_procs = len(procs)

        if key in (ord("q"), ord("Q")):
            self.stop()
            return False

        if key in (ord("j"), KeyCode.DOWN):
            if total_procs > 0:
                self._selected = min(total_procs - 1, self._selected + 1)
            return True

        if key in (ord("k"), KeyCode.UP):
            if total_procs > 0:
                self._selected = max(0, self._selected - 1)
            return True

        if key in (ord("s"), ord("S")):
            self._model.cycle_sort()
            return True

        if key in (ord(" "),):
            self._model.toggle_pause()
            return True

        if key in (ord("d"), ord("x"), KeyCode.DELETE):
            self._model.kill_process(self._selected)
            if self._selected >= len(self._model.get_processes()):
                self._selected = max(0, len(self._model.get_processes()) - 1)
            return True

        if key in (ord("n"), ord("a")):
            self._input_mode = True
            self._input_buffer = ""
            return True

        return True


def create_monitor_app(adapter: Optional[ITuiAdapter] = None) -> TuiApplication:
    real_adapter = adapter if adapter is not None else CursesAdapter()
    model = SystemMonitorModel()
    view = SystemMonitorView(real_adapter, model)
    header_view = SystemHeaderDashboardView(real_adapter, model)
    table_view = ProcessTableView(real_adapter, model)
    controller = SystemMonitorController(model, view, real_adapter)

    builder = ApplicationBuilder()
    app = (
        builder
        .set_adapter(real_adapter)
        .set_model(model)
        .add_view(header_view)
        .add_view(table_view)
        .add_view(view)
        .set_controller(controller)
        .build()
    )
    return app


def main() -> None:
    app = create_monitor_app()
    app.run()


if __name__ == "__main__":
    main()
