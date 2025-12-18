import tkinter as tk


class BoundingBoxSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Transparent overlay
        self.root.configure(bg='gray')

        self.canvas = tk.Canvas(self.root, cursor="cross", bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bbox = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.root.quit())

        print("Draw a rectangle on screen. Press ESC to cancel.")

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        width = x2 - x1
        height = y2 - y1

        self.bbox = (x1, y1, width, height)
        self.root.quit()

    def get_bbox(self):
        self.root.mainloop()
        self.root.destroy()
        return self.bbox


# Usage
selector = BoundingBoxSelector()
bbox = selector.get_bbox()

if bbox:
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    print(f"Bounding Box: ({bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]})")