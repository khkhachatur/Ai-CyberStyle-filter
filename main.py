from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox

from filters.pipeline import apply_filters_sequence

# Preview size
PREVIEW_W = 420
PREVIEW_H = 420


class CyberFilterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------- WINDOW SETUP ----------
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")  # built-in theme, fits cyber style

        self.title("AI CyberStyle Filter")
        self.geometry("980x540")
        self.minsize(900, 520)

        # data
        self.main_image_path: str | None = None
        self.face_image_path: str | None = None
        self.last_output_path: str | None = None

        self.preview_main_ctkimg = None
        self.preview_out_ctkimg = None

        # ---------- LAYOUT: 2 COLUMNS ----------
        self.grid_columnconfigure(0, weight=0)   # left panel
        self.grid_columnconfigure(1, weight=1)   # right panel
        self.grid_rowconfigure(0, weight=1)

        # Left control panel
        self._build_left_panel()

        # Right preview panel
        self._build_right_panel()

    # =========================
    # UI BUILDERS
    # =========================
    def _build_left_panel(self):
        left = ctk.CTkFrame(self, corner_radius=16)
        left.grid(row=0, column=0, sticky="nsw", padx=12, pady=12)

        # Make it a bit wider
        left.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            left,
            text="AI CyberStyle Filter",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=16, pady=(14, 4), sticky="w")

        subtitle = ctk.CTkLabel(
            left,
            text="Upload main photo, optional face photo,\nthen apply the full filter pipeline.",
            font=ctk.CTkFont(size=12)
        )
        subtitle.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        # ---- MAIN IMAGE SECTION ----
        main_frame = ctk.CTkFrame(left, corner_radius=12, fg_color=("gray14", "gray15"))
        main_frame.grid(row=2, column=0, padx=12, pady=(4, 8), sticky="ew")
        main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            main_frame,
            text="Main Outfit Image",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.main_path_label = ctk.CTkLabel(
            main_frame,
            text="No file selected",
            font=ctk.CTkFont(size=11),
            text_color="gray80"
        )
        self.main_path_label.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="w")

        ctk.CTkButton(
            main_frame,
            text="Select Main Image",
            command=self.on_select_main,
            height=32
        ).grid(row=2, column=0, padx=12, pady=(4, 10), sticky="ew")

        # ---- OPTIONAL FACE IMAGE SECTION ----
        face_frame = ctk.CTkFrame(left, corner_radius=12, fg_color=("gray14", "gray15"))
        face_frame.grid(row=3, column=0, padx=12, pady=(4, 8), sticky="ew")
        face_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            face_frame,
            text="Face Image (optional)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.face_path_label = ctk.CTkLabel(
            face_frame,
            text="Will auto-crop from main image\nif not provided.",
            font=ctk.CTkFont(size=11),
            text_color="gray80",
            justify="left"
        )
        self.face_path_label.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="w")

        ctk.CTkButton(
            face_frame,
            text="Select Face Image",
            command=self.on_select_face,
            height=32
        ).grid(row=2, column=0, padx=12, pady=(4, 10), sticky="ew")

        # ---- ACTIONS ----
        actions = ctk.CTkFrame(left, corner_radius=12, fg_color=("gray14", "gray15"))
        actions.grid(row=4, column=0, padx=12, pady=(8, 12), sticky="ew")
        actions.grid_columnconfigure(0, weight=1)

        self.process_button = ctk.CTkButton(
            actions,
            text="▶ Apply Cyber Filter",
            fg_color="#00b894",
            hover_color="#019870",
            height=38,
            command=self.on_apply_filters
        )
        self.process_button.grid(row=0, column=0, padx=12, pady=(10, 6), sticky="ew")

        self.status_label = ctk.CTkLabel(
            actions,
            text="Ready.",
            font=ctk.CTkFont(size=11),
            text_color="gray80"
        )
        self.status_label.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")
        # ---- CUSTOM ID SECTION ----
        ctk.CTkLabel(
            actions,
            text=None,
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.custom_id_entry = ctk.CTkEntry(
            actions,
            placeholder_text="Enter ID (optional)",
            height=32
        )
        self.custom_id_entry.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")


    def _build_right_panel(self):
        right = ctk.CTkFrame(self, corner_radius=16)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)

        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            right,
            text="Preview",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        # inner frame with two previews (original / filtered)
        preview_container = ctk.CTkFrame(right, corner_radius=14, fg_color=("gray14", "gray15"))
        preview_container.grid(row=1, column=0, padx=16, pady=(4, 16), sticky="nsew")
        preview_container.grid_columnconfigure((0, 1), weight=1)
        preview_container.grid_rowconfigure(1, weight=1)

        # Left: main image
        ctk.CTkLabel(
            preview_container,
            text="Main Image",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.main_preview_label = ctk.CTkLabel(
            preview_container,
            text="No image",
            anchor="center"
        )
        self.main_preview_label.grid(row=1, column=0, padx=12, pady=8, sticky="nsew")

        # Right: output image
        ctk.CTkLabel(
            preview_container,
            text="Filtered Output",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, padx=12, pady=(10, 4), sticky="w")

        self.out_preview_label = ctk.CTkLabel(
            preview_container,
            text="No output yet",
            anchor="center"
        )
        self.out_preview_label.grid(row=1, column=1, padx=12, pady=8, sticky="nsew")

    # =========================
    # IMAGE HELPERS
    # =========================
    def _load_ctk_image(self, path, max_w=PREVIEW_W, max_h=PREVIEW_H):
        if not path or not os.path.exists(path):
            return None

        img = Image.open(path).convert("RGB")
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

    def _update_main_preview(self):
        if not self.main_image_path:
            self.main_preview_label.configure(text="No image", image=None)
            return

        self.preview_main_ctkimg = self._load_ctk_image(self.main_image_path)
        if self.preview_main_ctkimg:
            self.main_preview_label.configure(image=self.preview_main_ctkimg, text="")
        else:
            self.main_preview_label.configure(text="Failed to load", image=None)

    def _update_output_preview(self):
        if not self.last_output_path:
            self.out_preview_label.configure(text="No output yet", image=None)
            return

        self.preview_out_ctkimg = self._load_ctk_image(self.last_output_path)
        if self.preview_out_ctkimg:
            self.out_preview_label.configure(image=self.preview_out_ctkimg, text="")
        else:
            self.out_preview_label.configure(text="Failed to load", image=None)

    # =========================
    # CALLBACKS
    # =========================
    def on_select_main(self):
        path = filedialog.askopenfilename(
            title="Select main outfit image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        self.main_image_path = path
        self.main_path_label.configure(
            text=Path(path).name
        )
        self._update_main_preview()
        self.status_label.configure(text="Main image loaded.")

    def on_select_face(self):
        path = filedialog.askopenfilename(
            title="Select face image (optional)",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        self.face_image_path = path
        self.face_path_label.configure(
            text=f"Face image: {Path(path).name}"
        )
        self.status_label.configure(text="Face image loaded.")

    def on_apply_filters(self):
        if not self.main_image_path:
            messagebox.showinfo("No image", "Please select a main image first.")
            return

        self.status_label.configure(text="Running pipeline...", text_color="#00ffb3")
        self.process_button.configure(state="disabled")
        
        custom_id = self.custom_id_entry.get().strip().upper()

        out_path = apply_filters_sequence(
            self.main_image_path,
            face_path=self.face_image_path,
            id_value=custom_id if custom_id else "UNKNOWN"
        )

        print("Pipeline output path:", out_path)

        self.last_output_path = out_path
        self._update_output_preview()

        self.status_label.configure(
            text=f"Done. Saved as {Path(out_path).name}",
            text_color="gray80"
        )

        self.process_button.configure(state="normal")


if __name__ == "__main__":
    app = CyberFilterApp()
    app.mainloop()
