"""Full-screen bounding box selector overlay."""

import tkinter as tk
from typing import Optional, Tuple

Region = Tuple[int, int, int, int]  # (x, y, width, height)


class BoundingBoxSelector:
    """Full-screen overlay for drawing a bounding box region."""

    MIN_SELECTION_SIZE = 10  # Minimum pixels for valid selection

    def __init__(self):
        self._bbox: Optional[Region] = None
        self._start_x: int = 0
        self._start_y: int = 0
        self._rect_id: Optional[int] = None

    def select(self) -> Optional[Region]:
        """
        Open selector overlay and wait for user to draw a region.

        Returns:
            Tuple of (x, y, width, height) or None if cancelled.
        """
        root = tk.Tk()
        root.attributes("-fullscreen", True)
        root.attributes("-alpha", 0.3)
        root.configure(bg="gray")

        canvas = tk.Canvas(root, cursor="cross", bg="gray", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        self._add_instructions(root)
        self._bind_events(canvas, root)

        root.mainloop()
        root.destroy()
        return self._bbox

    def _add_instructions(self, root: tk.Tk) -> None:
        label = tk.Label(
            root,
            text="Draw a rectangle to select the region. Press ESC to cancel.",
            font=("Arial", 14),
            bg="gray",
            fg="white"
        )
        label.place(relx=0.5, y=30, anchor="center")

    def _bind_events(self, canvas: tk.Canvas, root: tk.Tk) -> None:
        canvas.bind("<ButtonPress-1>", lambda e: self._on_press(e, canvas))
        canvas.bind("<B1-Motion>", lambda e: self._on_drag(e, canvas))
        canvas.bind("<ButtonRelease-1>", lambda e: self._on_release(e, root))
        root.bind("<Escape>", lambda e: root.quit())

    def _on_press(self, event: tk.Event, canvas: tk.Canvas) -> None:
        self._start_x, self._start_y = event.x, event.y
        self._rect_id = canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline="red", width=3
        )

    def _on_drag(self, event: tk.Event, canvas: tk.Canvas) -> None:
        if self._rect_id:
            canvas.coords(self._rect_id, self._start_x, self._start_y, event.x, event.y)

    def _on_release(self, event: tk.Event, root: tk.Tk) -> None:
        x1, x2 = sorted([self._start_x, event.x])
        y1, y2 = sorted([self._start_y, event.y])
        width, height = x2 - x1, y2 - y1

        if width > self.MIN_SELECTION_SIZE and height > self.MIN_SELECTION_SIZE:
            self._bbox = (x1, y1, width, height)
        root.quit()


# Allow standalone usage for testing
if __name__ == "__main__":
    selector = BoundingBoxSelector()
    bbox = selector.select()
    if bbox:
        print(f"Selected region: {bbox}")
    else:
        print("Selection cancelled")
