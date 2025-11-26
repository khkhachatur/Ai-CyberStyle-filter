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


#  AI OVERLAY (face HUD + body HUD + GPT clothing labels)
def apply_ai_overlay(image_pil, labels_offset_y=None):
    """
    Detects face + body, draws HUD boxes,
    generates clothing labels using GPT Vision.

    Returns:
        main_image_with_all_huds, face_frame_bbox
    """

    face_bbox = detect_face(image_pil)
    body_bbox = detect_body(image_pil, model_body)

    out = image_pil.copy()
    face_frame_bbox = None

    # ---- BODY HUD + TEXT ----
    if body_bbox:
        w, h = out.size
        bx1, by1, bx2, by2 = _make_body_bbox(
            body_bbox[0], body_bbox[1], body_bbox[2], body_bbox[3],
            w, h, pad_ratio=0.10
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

    # ---- FACE HUD ----
    if face_bbox:
        out, face_frame_bbox = draw_face_box(out, face_bbox)

    return out, face_frame_bbox



#  Saving final image (borders only)
def save_filtered_image(img, src_path):
    base, _ = os.path.splitext(src_path)
    out_path = base + "_filtered.png"

    img = draw_borders_and_labels(img)
    img.save(out_path, format="PNG")

    return out_path



#  FULL PIPELINE
def apply_filters_sequence(path, face_path=None, id_value="UNKNOWN"):
    # 1) Load + style
    img = Image.open(path).convert("RGB")
    img = apply_stylistic_pipeline(img)

    w, h = img.size

    # 2) Prepare face for PROFILE card
    if face_path:
        face_img = Image.open(face_path).convert("RGB")
    else:
        main_face_bbox = detect_face(img)
        face_img = extract_face_crop(img, main_face_bbox) if main_face_bbox else None

    face_card = make_face_card(face_img, id_value=id_value) if face_img is not None else None


    # 3) Decide PROFILE card placement
    labels_offset_y = None
    card_x = card_y = None

    body_bbox_for_side = detect_body(img, model_body)
    body_center_x = (body_bbox_for_side[0] + body_bbox_for_side[2]) / 2 if body_bbox_for_side else w/2

    if face_card is not None:
        place_card_right = body_center_x < (w / 2)
        side_margin = 60
        top_margin = 110

        card_x = w - face_card.width - side_margin if place_card_right else side_margin
        card_y = top_margin

        labels_offset_y = card_y + face_card.height + 30

    # 4) Run overlays
    img, face_frame_bbox = apply_ai_overlay(img, labels_offset_y=labels_offset_y)

    draw = ImageDraw.Draw(img)

    # 5) Paste PROFILE card
    if face_card is not None and card_x is not None:
        img.paste(face_card, (card_x, card_y))

    # 5b) Draw connector line (only if face_frame_bbox exists)
    if face_card is not None and card_x is not None and face_frame_bbox is not None:
        fx1, fy1, fx2, fy2 = face_frame_bbox

        # Midpoint Y for smooth alignment
        frame_mid_y = (fy1 + fy2) // 2
        card_mid_y = card_y + face_card.height // 2

        if place_card_right:
            frame_anchor_x = fx2               
            card_anchor_x  = card_x            
        else:
            frame_anchor_x = fx1              
            card_anchor_x  = card_x + face_card.width   

        frame_anchor_y = frame_mid_y
        card_anchor_y  = card_mid_y

        # Draw connector line
        draw.line(
            (frame_anchor_x, frame_anchor_y,
            card_anchor_x, card_anchor_y),
            fill=GREEN,
            width=3
        )





    # 6) Save final image
    out_path = save_filtered_image(img, path)
    return out_path
