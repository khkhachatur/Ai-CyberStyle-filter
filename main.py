from dotenv import load_dotenv
load_dotenv()

from tkinter import Tk, ttk, messagebox, filedialog
from ui.filter_ui import attach_filter_ui
from ui.preview_renderer import render_preview

class ImageUploader(Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Cyber Filter")
        self.geometry("520x420")

        self.images = []
        self.photo_cache = {}

        ctrl = ttk.Frame(self)
        ctrl.pack(padx=10, pady=10, fill="x")

        ttk.Label(ctrl, text="Choose image:").grid(row=0, column=0)
        self.combo = ttk.Combobox(ctrl, state="readonly", width=50)
        self.combo.grid(row=1, column=0, columnspan=2)
        self.combo.bind("<<ComboboxSelected>>", self.on_select)

        ttk.Button(ctrl, text="Upload...", command=self.upload).grid(row=1, column=2)
        ttk.Button(ctrl, text="Remove", command=self.remove).grid(row=1, column=3)

        preview_frame = ttk.LabelFrame(self, text="Preview")
        preview_frame.pack(padx=10, pady=10)

        self.preview = ttk.Label(preview_frame)
        self.preview.pack()

        attach_filter_ui(self, self)

    def upload(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        self.images.append(path)
        self.combo["values"] = [p.split("/")[-1] for p in self.images]
        self.combo.current(len(self.images)-1)
        self.show_image(path)

    def remove(self):
        idx = self.combo.current()
        if idx < 0:
            return
        self.images.pop(idx)
        self.combo["values"] = [p.split("/")[-1] for p in self.images]
        self.preview.config(image="")

    def on_select(self, *_):
        idx = self.combo.current()
        if idx >= 0:
            self.show_image(self.images[idx])

    def show_image(self, path):
        img = render_preview(path)
        self.preview.config(image=img)
        self.photo_cache[path] = img

if __name__ == "__main__":
    ImageUploader().mainloop()
