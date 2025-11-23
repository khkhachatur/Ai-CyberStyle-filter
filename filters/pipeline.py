from PIL import Image
import os

from filters.stylistic_filters import apply_stylistic_pipeline
from filters.border_drawer import draw_borders_and_labels

from filters.detector import detect_face, model_face, model_body
from filters.body_frame import detect_body, draw_body_box

from filters.detector import detect_face
from filters.face_frame import (
    draw_face_box,
    extract_face_crop,
    render_face_frame
)

def apply_ai_overlay(image_pil):
    face_bbox = detect_face(image_pil)
    body_bbox = detect_body(image_pil, model_body)

    out = image_pil

    if body_bbox:
        out = draw_body_box(out, body_bbox, face_bbox)

    if face_bbox:
        out = draw_face_box(out, face_bbox)

    face_crop = extract_face_crop(image_pil, face_bbox) if face_bbox else None
    face_frame = render_face_frame(face_crop) if face_crop else None

    return out, face_frame





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
