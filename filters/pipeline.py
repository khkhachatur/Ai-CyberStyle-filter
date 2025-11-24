# filters/pipeline.py

import os
from PIL import Image

from filters.stylistic_filters import apply_stylistic_pipeline
from filters.border_drawer import draw_borders_and_labels

from filters.detector import detect_face, model_face, model_body
from filters.face_frame import (
    draw_face_box,
    extract_face_crop,
    render_face_frame,
)
from filters.body_frame import detect_body, draw_body_box, _make_body_bbox
from filters.clothing_ai import analyze_clothing_with_gpt


def apply_ai_overlay(image_pil):
    """
    Detects face + body, draws HUD boxes, generates face-frame,
    and uses GPT Vision to create clothing labels.
    Returns:
        (main_image_with_overlays, face_frame_image)
    """
    # ---- 1) Face detection ----
    face_bbox = detect_face(image_pil)

    # ---- 2) Body detection (using general YOLO model) ----
    body_bbox = detect_body(image_pil, model_body)

    out = image_pil

    # ---- 3) If body detected → crop & call GPT Vision ----
    top_label = None
    bottom_label = None

    if body_bbox is not None:
        w, h = image_pil.size
        bx1, by1, bx2, by2 = _make_body_bbox(
            body_bbox[0],
            body_bbox[1],
            body_bbox[2],
            body_bbox[3],
            w,
            h,
            pad_ratio=0.10,
        )
        body_crop = image_pil.crop((bx1, by1, bx2, by2))

        # GPT Vision call is wrapped in try/except so your app
        # keeps working even if the API fails or env is missing.
        try:
            top_desc, bottom_desc = analyze_clothing_with_gpt(body_crop)
            top_label = f"TOP: {top_desc}"
            bottom_label = f"BOTTOM: {bottom_desc}"
        except Exception:
            top_label = "TOP: AI GENERATED TEXT"
            bottom_label = "BOTTOM: AI GENERATED TEXT"

        # Draw body HUD with labels
        out = draw_body_box(
            out,
            body_bbox,
            face_bbox=face_bbox,
            top_text=top_label,
            bottom_text=bottom_label,
        )

    # ---- 4) Face HUD ----
    if face_bbox is not None:
        out = draw_face_box(out, face_bbox)

    # ---- 5) Face frame panel ----
    face_crop = extract_face_crop(image_pil, face_bbox) if face_bbox is not None else None
    face_frame = render_face_frame(face_crop) if face_crop is not None else None

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

    # Run AI overlay (face + body + labels)
    img, _ = apply_ai_overlay(img)

    # Save full filtered image
    out_path = save_filtered_image(img, path)
    return out_path
