import tkinter as tk
from tkinter import ttk, messagebox
import threading

from ..config import NavAIConfig, load_config, save_config
from ..executor import execute_goal, ExecutionError
from .bbox_selector import BoundingBoxSelector
from .log_panel import LogPanel


class NavAILauncher:
    #Main application window orchestrating all UI components.

    WINDOW_SIZE = "600x500"
    MIN_SIZE = (500, 400)
    POLL_INTERVAL_MS = 100

    def __init__(self):
        self.config = load_config()
        self.is_running = False

        self.root = tk.Tk()
        self._setup_window()
        self._create_widgets()
        self._update_region_display()
        self._start_polling()

    def _setup_window(self) -> None:
        self.root.title("NavAI Launcher")
        self.root.geometry(self.WINDOW_SIZE)
        self.root.minsize(*self.MIN_SIZE)
        self._center_window()

    def _center_window(self) -> None:
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 600) // 2
        y = (self.root.winfo_screenheight() - 500) // 2
        self.root.geometry(f"+{x}+{y}")

    def _create_widgets(self) -> None:
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_header(main_frame)
        self._create_region_section(main_frame)
        self._create_goal_section(main_frame)
        self._create_buttons(main_frame)
        self._create_log_panel(main_frame)
        self._create_status_bar()

    def _create_header(self, parent: ttk.Frame) -> None:
        title = ttk.Label(parent, text="NavAI", font=("Arial", 18, "bold"))
        title.pack(pady=(0, 15))

    def _create_region_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Screen Region", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.region_label = ttk.Label(frame, text="", font=("Consolas", 10))
        self.region_label.pack(side=tk.LEFT, padx=(0, 10))

        self.select_region_btn = ttk.Button(
            frame, text="Select Region", command=self._on_select_region
        )
        self.select_region_btn.pack(side=tk.RIGHT)

    def _create_goal_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Goal", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.goal_entry = ttk.Entry(frame, font=("Arial", 11))
        self.goal_entry.pack(fill=tk.X)
        self.goal_entry.insert(0, self.config.last_goal)
        self.goal_entry.bind("<Return>", lambda e: self._on_run())

    def _create_buttons(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 10))

        self.run_btn = ttk.Button(frame, text="Run", command=self._on_run)
        self.run_btn.pack(side=tk.RIGHT, padx=(10, 0))

        clear_btn = ttk.Button(frame, text="Clear Logs", command=lambda: self.log_panel.clear())
        clear_btn.pack(side=tk.RIGHT, padx=(10, 0))

        quit_btn = ttk.Button(frame, text="Quit", command=self._on_quit)
        quit_btn.pack(side=tk.RIGHT)

    def _create_log_panel(self, parent: ttk.Frame) -> None:
        self.log_panel = LogPanel(parent)
        self.log_panel.pack(fill=tk.BOTH, expand=True)
        self.log_panel.start_capture()

    def _create_status_bar(self) -> None:
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _start_polling(self) -> None:
        """Start polling the log queue."""
        self.log_panel.poll()
        self.root.after(self.POLL_INTERVAL_MS, self._start_polling)

    def _update_region_display(self) -> None:
        if self.config.is_region_configured():
            x, y, w, h = self.config.region
            self.region_label.config(text=f"({x}, {y}, {w}, {h})")
            self.select_region_btn.config(text="Change Region")
        else:
            self.region_label.config(text="Not configured")

    def _set_ui_enabled(self, enabled: bool) -> None:
        """Enable or disable interactive elements."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.run_btn.config(state=state)
        self.select_region_btn.config(state=state)
        self.goal_entry.config(state=state)
        self.is_running = not enabled

    # Event Handlers

    def _on_select_region(self) -> None:
        self.root.withdraw()

        selector = BoundingBoxSelector()
        bbox = selector.select()

        self.root.deiconify()

        if bbox:
            self.config = NavAIConfig(region=bbox, last_goal=self.goal_entry.get())
            save_config(self.config)
            self._update_region_display()
            self.log_panel.info(f"Region updated: {bbox}")
            self.status_var.set("Region configured")
        else:
            self.log_panel.info("Region selection cancelled")

    def _on_run(self) -> None:
        if self.is_running:
            return

        goal = self.goal_entry.get().strip()

        if not goal:
            messagebox.showwarning("Input Required", "Please enter a goal.")
            return

        if not self.config.is_region_configured():
            messagebox.showwarning("Region Required", "Please select a screen region first.")
            return

        # Persist state
        self.config = NavAIConfig(region=self.config.region, last_goal=goal)
        save_config(self.config)

        self.log_panel.info(f"Starting: '{goal}'")
        self.status_var.set("Running...")
        self._set_ui_enabled(False)

        # Execute in background thread
        thread = threading.Thread(
            target=self._execute_in_thread,
            args=(goal, self.config.region),
            daemon=True
        )
        thread.start()

    def _execute_in_thread(self, goal: str, region: tuple) -> None:
        """Run execution in background thread."""
        try:
            category = execute_goal(goal, region)
            self.root.after(0, lambda: self.log_panel.info(f"Category: {category}"))
            self.root.after(0, lambda: self.log_panel.success("Execution complete"))
            self.root.after(0, lambda: self.status_var.set("Complete"))
        except ExecutionError as e:
            self.root.after(0, lambda: self.log_panel.error(str(e)))
            self.root.after(0, lambda: self.status_var.set("Error"))
        except Exception as e:
            self.root.after(0, lambda: self.log_panel.error(f"Unexpected error: {e}"))
            self.root.after(0, lambda: self.status_var.set("Error"))
        finally:
            self.root.after(0, lambda: self._set_ui_enabled(True))

    def _on_quit(self) -> None:
        self.log_panel.stop_capture()
        self.root.quit()

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run(self) -> None:
        """Start the application."""
        self.log_panel.info("NavAI Launcher started")
        self.root.mainloop()
