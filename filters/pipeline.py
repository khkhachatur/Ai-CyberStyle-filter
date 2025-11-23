from PIL import Image
import os

from filters.stylistic_filters import apply_stylistic_pipeline
from filters.border_drawer import draw_borders_and_labels

from filters.detector import detect_face
from filters.face_frame import (
    draw_face_box,
    extract_face_crop,
    render_face_frame
)

def apply_ai_overlay(image_pil):
    """
    Detects face, draws box, generates face-frame image.
    Returns:
        (main_image_with_box, face_frame_image)
    """
    bbox = detect_face(image_pil)

    if bbox is None:
        return image_pil, None

    # Draw green rectangle
    img_with_box = draw_face_box(image_pil, bbox)

    # Extract and crop face
    face_crop = extract_face_crop(image_pil, bbox)

    # Render green face window
    face_frame = render_face_frame(face_crop)

    return img_with_box, face_frame


def save_filtered_image(img, src_path):
    base, _ = os.path.splitext(src_path)
    out_path = base + "_filtered.png"

    img = draw_borders_and_labels(img)
    img.save(out_path, format="PNG")

    return out_path


def apply_filters_sequence(path):
    img = Image.open(path).convert("RGB")
    img = apply_stylistic_pipeline(img)

    # Run AI overlay
    img, _ = apply_ai_overlay(img)

    # Save full filtered image
    out_path = save_filtered_image(img, path)
    return out_path
