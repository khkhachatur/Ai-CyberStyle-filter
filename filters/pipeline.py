import os
from PIL import Image
from .stylistic_filters import apply_stylistic_pipeline
from .border_drawer import draw_borders_and_labels

def save_filtered_image(img, src_path):
    base, _ = os.path.splitext(src_path)
    out_path = base + "_filtered.png"

    img = draw_borders_and_labels(img)
    img.save(out_path, format="PNG")

    return out_path

def apply_filters_sequence(path):
    img = Image.open(path).convert("RGB")
    img = apply_stylistic_pipeline(img)
    out_path = save_filtered_image(img, path)
    return out_path
