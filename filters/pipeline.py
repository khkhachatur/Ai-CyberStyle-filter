# filters/pipeline.py

import os
from PIL import Image

# --- internal filters ---
from filters.stylistic_filters import apply_stylistic_pipeline
from filters.border_drawer import draw_borders_and_labels

# Face detection (YOLO face model)
from filters.detector import detect_face, model_face, model_body

# Face HUD + face crop + face mini-frame
from filters.face_frame import (
    draw_face_box,
    extract_face_crop,
    render_face_frame,
)

# Face card (green ID card on the left)
from filters.face_card import make_face_card

# Body HUD + clothing labels
from filters.body_frame import (
    detect_body,
    draw_body_box,
    _make_body_bbox
)

# GPT Vision clothing description
from filters.clothing_ai import analyze_clothing_with_gpt



# --------------------------------------------------------------------
#  AI OVERLAY (face HUD + body HUD + GPT clothing labels)
# --------------------------------------------------------------------
def apply_ai_overlay(image_pil):
    """
    Detects face + body, draws HUD boxes,
    generates clothing labels using GPT Vision,
    creates the face-frame (small square panel).

    Returns:
        main_image_with_all_huds, face_frame_image
    """

    # --------------------
    # 1. Face detection
    # --------------------
    face_bbox = detect_face(image_pil)

    # --------------------
    # 2. Body detection
    # --------------------
    body_bbox = detect_body(image_pil, model_body)

    out = image_pil

    # --------------------
    # 3. Clothing AI (GPT Vision)
    # --------------------
    top_label = None
    bottom_label = None

    if body_bbox:
        w, h = image_pil.size
        bx1, by1, bx2, by2 = _make_body_bbox(
            body_bbox[0], body_bbox[1], body_bbox[2], body_bbox[3],
            w, h, pad_ratio=0.10
        )

        body_crop = image_pil.crop((bx1, by1, bx2, by2))

        # GPT Clothing (safe fallback)
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

    # --------------------
    # 4. Draw Face HUD
    # --------------------
    if face_bbox:
        out = draw_face_box(out, face_bbox)

    # --------------------
    # 5. Face Frame Panel
    # --------------------
    face_crop = extract_face_crop(image_pil, face_bbox) if face_bbox else None
    face_frame = render_face_frame(face_crop) if face_crop else None

    return out, face_frame



# --------------------------------------------------------------------
#  Saving final image (with optional face card)
# --------------------------------------------------------------------
def save_filtered_image(img, src_path, face_card=None):
    """
    Draw borders + overlay the face-card if provided + save file.
    """
    base, _ = os.path.splitext(src_path)
    out_path = base + "_filtered.png"

    # Paste face card before border lines
    if face_card:
        img.paste(face_card, (40, 100))

    img = draw_borders_and_labels(img)
    img.save(out_path, format="PNG")

    return out_path



# --------------------------------------------------------------------
#  FULL PIPELINE (main entry point)
# --------------------------------------------------------------------
def apply_filters_sequence(path, face_path=None):
    """
    1. Loads image
    2. Applies stylistic filters
    3. Runs AI HUD overlays
    4. Generates optional face-card (auto or user)
    5. Saves final result
    """

    # Load main image
    img = Image.open(path).convert("RGB")

    # Apply global style
    img = apply_stylistic_pipeline(img)

    # AI overlays (face HUD + body HUD + GPT labels)
    img, _ = apply_ai_overlay(img)

    # ----- Face card selection -----
    if face_path:
        # User provided second image
        face_img = Image.open(face_path).convert("RGB")
    else:
        # Auto-crop face from processed main image
        face_bbox = detect_face(img)
        face_img = extract_face_crop(img, face_bbox) if face_bbox else None

    # Build face card BEFORE saving
    face_card = make_face_card(face_img) if face_img else None

    # Save final image with face card
    out_path = save_filtered_image(img, path, face_card=face_card)

    return out_path
