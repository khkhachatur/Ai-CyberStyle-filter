from tkinter import ttk, messagebox
from filters.pipeline import apply_filters_sequence
import os

def attach_filter_ui(root, app):
    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=(0,6), fill="x")

    ttk.Label(frame, text="Filters:").grid(row=0, column=0)
    ttk.Button(frame, text="Apply Filters", command=lambda: run_pipeline(app)).grid(row=0, column=1)

def run_pipeline(app):
    idx = app.combo.current()
    if idx < 0:
        messagebox.showinfo("No image", "Select an image first.")
        return

    path = app.images[idx]
    new_path = apply_filters_sequence(path)

    app.images.append(new_path)
    app.combo["values"] = [os.path.basename(p) for p in app.images]
    app.combo.current(len(app.images)-1)
    app.show_image(new_path)
