import os
from pathlib import Path

from PIL import Image, ImageDraw

from filters.stylistic_filters import apply_stylistic_pipeline
from filters.border_drawer import draw_borders_and_labels

from filters.detector import detect_face, model_body
from filters.face_frame import (
    draw_face_box,
    extract_face_crop,
    GREEN,
)
from filters.face_card import make_face_card
from filters.body_frame import (
    detect_body,
    draw_body_box,
    _make_body_bbox,
)
from filters.clothing_ai import analyze_clothing_with_gpt


# --------------------------------------------------------------------
#  AI OVERLAY (face HUD + body HUD + GPT clothing labels)
# --------------------------------------------------------------------
def apply_ai_overlay(image_pil, labels_offset_y=None):
    """
    Detects face + body, draws HUD boxes,
    generates clothing labels using GPT Vision.

    Returns:
        main_image_with_all_huds, face_frame_image (currently unused)
    """

    # 1) Detect face and body
    face_bbox = detect_face(image_pil)
    body_bbox = detect_body(image_pil, model_body)

    out = image_pil.copy()

    # 2) Clothing AI (GPT Vision) + body HUD
    top_label = None
    bottom_label = None

    if body_bbox:
        w, h = out.size
        bx1, by1, bx2, by2 = _make_body_bbox(
            body_bbox[0],
            body_bbox[1],
            body_bbox[2],
            body_bbox[3],
            w,
            h,
            pad_ratio=0.10,
        )

        body_crop = out.crop((bx1, by1, bx2, by2))

        try:
            top_desc, bottom_desc = analyze_clothing_with_gpt(body_crop)
            top_label = f"TOP: {top_desc}"
            bottom_label = f"BOTTOM: {bottom_desc}"
        except Exception:
            top_label = "TOP: AI GENERATED TEXT"
            bottom_label = "BOTTOM: AI GENERATED TEXT"

        out = draw_body_box(
            out,
            body_bbox,
            face_bbox=face_bbox,
            top_text=top_label,
            bottom_text=bottom_label,
            labels_offset_y=labels_offset_y,
        )

    # 3) Face HUD box on the main image
    if face_bbox:
        out = draw_face_box(out, face_bbox)

    # 4) Optional separate face_frame for future use
    face_crop = extract_face_crop(image_pil, face_bbox) if face_bbox else None
    face_frame = None  # you can call render_face_frame(face_crop) if you ever need it

    return out, face_frame


# --------------------------------------------------------------------
#  Saving final image (borders only)
# --------------------------------------------------------------------
def save_filtered_image(img, src_path):
    """
    Draw borders + labels and save PNG next to original.
    """
    base, _ = os.path.splitext(src_path)
    out_path = base + "_filtered.png"

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
    3. Prepares face image (user or auto)
    4. Builds PROFILE face-card and decides its position
    5. Runs AI HUD overlays (with label offset below card)
    6. Draws a diagonal line from card to body
    7. Draws borders and saves final result
    """

    # 1) Load + style
    img = Image.open(path).convert("RGB")
    img = apply_stylistic_pipeline(img)

    w, h = img.size

    # 2) Prepare face image for card
    if face_path:
        face_img = Image.open(face_path).convert("RGB")
    else:
        main_face_bbox = detect_face(img)
        face_img = extract_face_crop(img, main_face_bbox) if main_face_bbox else None

    face_card = make_face_card(face_img) if face_img is not None else None

    # 3) Decide side for card, and compute labels_offset_y
    labels_offset_y = None
    card_x = card_y = None
    body_bbox_for_side = detect_body(img, model_body)

    if face_card is not None:
        # If body detected, choose opposite side
        if body_bbox_for_side:
            bx1, by1, bx2, by2 = body_bbox_for_side
            body_center_x = (bx1 + bx2) / 2
        else:
            body_center_x = w / 2

        place_card_right = body_center_x < (w / 2)

        side_margin = 60
        top_margin = 110

        card_x = w - face_card.width - side_margin if place_card_right else side_margin
        card_y = top_margin

        labels_offset_y = card_y + face_card.height + 30

    # 4) Run AI overlay with possible label offset
    img, _ = apply_ai_overlay(img, labels_offset_y=labels_offset_y)

    draw = ImageDraw.Draw(img)

    # 5) Paste PROFILE face-card + draw connector from card to body
    if face_card is not None and card_x is not None:
        img.paste(face_card, (card_x, card_y))

        if body_bbox_for_side:
            bx1, by1, bx2, by2 = body_bbox_for_side
            body_center_x = (bx1 + bx2) / 2
            body_anchor_y = by1 + int((by2 - by1) * 0.25)

            # Card anchor: mid of side closer to the body
            if body_center_x < (w / 2):
                # body on left, card on right → use left edge of card
                card_anchor_x = card_x
            else:
                # body on right, card on left → use right edge of card
                card_anchor_x = card_x + face_card.width

            card_anchor_y = card_y + face_card.height // 2

            draw.line(
                (card_anchor_x, card_anchor_y, body_center_x, body_anchor_y),
                fill=GREEN,
                width=2,
            )

    # 6) Save final image with borders
    out_path = save_filtered_image(img, path)
    return out_path
