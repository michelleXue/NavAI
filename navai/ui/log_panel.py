import sys
import queue
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
from typing import Optional

#Scrollable log panel with stdout/stderr capture.
#TODO: Need to refactor all stdout/stderr to logs
class LogRedirector:
    """Redirects stdout/stderr to a queue for thread-safe UI updates."""

    def __init__(self, log_queue: queue.Queue, stream_name: str = "stdout"):
        self.queue = log_queue
        self.stream_name = stream_name
        self.original = sys.stdout if stream_name == "stdout" else sys.stderr

    def write(self, message: str) -> None:
        if message.strip():
            self.queue.put((self.stream_name, message))
        self.original.write(message)

    def flush(self) -> None:
        self.original.flush()


class LogPanel(ttk.LabelFrame):
    """Scrollable log panel widget with color-coded output."""

    # Color scheme (dark theme)
    COLORS = {
        "bg": "#1e1e1e",
        "fg": "#d4d4d4",
        "timestamp": "#6a9955",
        "stdout": "#d4d4d4",
        "stderr": "#f14c4c",
        "info": "#3794ff",
        "success": "#23d18b",
    }

    def __init__(self, parent: tk.Widget, **kwargs):
        super().__init__(parent, text="Logs", padding=5, **kwargs)

        self._log_queue: queue.Queue = queue.Queue()
        self._original_stdout: Optional[object] = None
        self._original_stderr: Optional[object] = None

        self._create_widgets()
        self._configure_tags()

    def _create_widgets(self) -> None:
        self.text = ScrolledText(
            self,
            height=12,
            font=("Consolas", 9),
            state=tk.DISABLED,
            wrap=tk.WORD,
            bg=self.COLORS["bg"],
            fg=self.COLORS["fg"]
        )
        self.text.pack(fill=tk.BOTH, expand=True)

    def _configure_tags(self) -> None:
        for tag, color in self.COLORS.items():
            if tag not in ("bg", "fg"):
                self.text.tag_configure(tag, foreground=color)

    def start_capture(self) -> None:
        """Begin capturing stdout and stderr."""
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = LogRedirector(self._log_queue, "stdout")
        sys.stderr = LogRedirector(self._log_queue, "stderr")

    def stop_capture(self) -> None:
        """Stop capturing and restore original streams."""
        if self._original_stdout:
            sys.stdout = self._original_stdout
        if self._original_stderr:
            sys.stderr = self._original_stderr

    def poll(self) -> None:
        """Process pending log messages. Call this periodically from main loop."""
        while True:
            try:
                tag, message = self._log_queue.get_nowait()
                self.append(message, tag)
            except queue.Empty:
                break

    def append(self, message: str, tag: str = "stdout") -> None:
        """Append a message with timestamp."""
        self.text.config(state=tk.NORMAL)

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.text.insert(tk.END, f"{message}\n", tag)

        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.append(message, "info")

    def success(self, message: str) -> None:
        """Log a success message."""
        self.append(message, "success")

    def error(self, message: str) -> None:
        """Log an error message."""
        self.append(message, "stderr")

    def clear(self) -> None:
        """Clear all log content."""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
