from PIL import ImageDraw, ImageFont
from filters.face_frame import _make_square_bbox, GREEN  # GREEN reused


def detect_body(image_pil, yolo_model):
    """
    Detect the largest person in the frame with a YOLO model (class 0 = person).
    Returns (x1, y1, x2, y2) or None.
    """
    import numpy as np

    img_np = np.array(image_pil)
    results = yolo_model(img_np, verbose=False)

    if not results or len(results[0].boxes) == 0:
        return None

    persons = []
    for box in results[0].boxes:
        if int(box.cls[0]) != 0:
            continue
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        area = (x2 - x1) * (y2 - y1)
        persons.append((area, (x1, y1, x2, y2)))

    if not persons:
        return None

    _, body_box = max(persons, key=lambda x: x[0])
    return body_box


def _make_body_bbox(x1, y1, x2, y2, image_w, image_h, pad_ratio=0.10):
    """
    Rectangular padded bbox for full body (no squaring).
    """
    bw = x2 - x1
    bh = y2 - y1

    pad_w = bw * pad_ratio
    pad_h = bh * pad_ratio

    bx1 = max(0, int(x1 - pad_w))
    by1 = max(0, int(y1 - pad_h))
    bx2 = min(image_w, int(x2 + pad_w))
    by2 = min(image_h, int(y2 + pad_h))

    return bx1, by1, bx2, by2


def draw_body_box(
    image_pil,
    bbox,
    face_bbox=None,
    top_text=None,
    bottom_text=None,
    labels_offset_y=None,
):
    if bbox is None:
        return image_pil

    x1, y1, x2, y2 = bbox
    w, h = image_pil.size

    bx1, by1, bx2, by2 = _make_body_bbox(x1, y1, x2, y2, w, h, pad_ratio=0.10)

    # Avoid overlapping with face bbox vertically
    if face_bbox is not None:
        fx1, fy1, fx2, fy2 = face_bbox
        if by1 < fy2:
            by1 = fy2 + 20

    out = image_pil.copy()
    draw = ImageDraw.Draw(out)

    side_len = bx2 - bx1
    img_len = min(w, h)
    ratio = side_len / img_len
    t = 3 if ratio >= 0.15 else 2

    # Draw body bounding box
    draw.rectangle((bx1, by1, bx2, by2), outline=GREEN, width=t)

    # Decide label side
    body_center_x = (bx1 + bx2) / 2
    labels_on_right = body_center_x < (w / 2)

    # Label sizes
    base_label_w = 260
    label_h = 35
    gap = 25

    # Compute label X positions
    if labels_on_right:
        label_x1 = bx2 + gap
        label_x2 = label_x1 + base_label_w
    else:
        label_x2 = bx1 - gap
        label_x1 = label_x2 - base_label_w

    # Y positions of labels
    if labels_offset_y is not None:
        top_label_y1 = labels_offset_y
    else:
        top_label_y1 = by1 + 40

    bottom_label_y1 = top_label_y1 + label_h + 15

    # Clamp inside image bounds
    if label_x1 < 0:
        shift = -label_x1 + 10
        label_x1 += shift
        label_x2 += shift

    if label_x2 > w:
        shift = (label_x2 - w) + 10
        label_x1 -= shift
        label_x2 -= shift

    label_w = label_x2 - label_x1
    if label_w < 200:
        label_w = 200
    label_x2 = label_x1 + label_w

    # ---- FINAL CONNECTOR LOGIC (correct) ----
    body_mid_y = (by1 + by2) // 2
    label_mid_y = bottom_label_y1 + label_h // 2

    if labels_on_right:
        # Labels on right → start at RIGHT side, end at LEFT side
        connector_start_x = bx2
        connector_end_x = label_x1
    else:
        # Labels on left → start at LEFT side, end at RIGHT side
        connector_start_x = bx1
        connector_end_x = label_x2

    draw.line(
        (connector_start_x, body_mid_y + 20,
         connector_end_x, label_mid_y),
        fill=GREEN, width=t
    )

    # Draw label backgrounds
    draw.rectangle(
        (label_x1, top_label_y1, label_x2, top_label_y1 + label_h),
        fill=GREEN
    )
    draw.rectangle(
        (label_x1, bottom_label_y1, label_x2, bottom_label_y1 + label_h),
        fill=GREEN
    )

    # Draw text
    def draw_fitted_text(text, x, y):
        if not text:
            return
        for fsize in range(22, 10, -1):
            try:
                font = ImageFont.truetype("arial.ttf", fsize)
            except:
                font = ImageFont.load_default()
            tb = draw.textbbox((0,0), text, font=font)
            if tb[2] - tb[0] <= label_w - 20:
                draw.text((x+10, y+5), text, fill=(0,0,0), font=font)
                return
        draw.text((x+10, y+5), text, fill=(0,0,0), font=font)

    top_label = top_text or "TOP: AI GENERATED TEXT"
    bottom_label = bottom_text or "BOTTOM: AI GENERATED TEXT"

    draw_fitted_text(top_label, label_x1, top_label_y1)
    draw_fitted_text(bottom_label, label_x1, bottom_label_y1)

    return out
