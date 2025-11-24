from PIL import ImageDraw, ImageFont
from filters.face_frame import _make_square_bbox, GREEN

def detect_body(image_pil, yolo_model):
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
    bw = x2 - x1
    bh = y2 - y1

    pad_w = bw * pad_ratio
    pad_h = bh * pad_ratio

    bx1 = max(0, int(x1 - pad_w))
    by1 = max(0, int(y1 - pad_h))
    bx2 = min(image_w, int(x2 + pad_w))
    by2 = min(image_h, int(y2 + pad_h))

    return bx1, by1, bx2, by2



def draw_body_box(image_pil, bbox, face_bbox=None):
    if bbox is None:
        return image_pil

    x1, y1, x2, y2 = bbox
    w, h = image_pil.size

    bx1, by1, bx2, by2 = _make_body_bbox(x1, y1, x2, y2, w, h, pad_ratio=0.10)

    if face_bbox is not None:
        fx1, fy1, fx2, fy2 = face_bbox
        if by1 < fy2:
            by1 = fy2 + 20

    out = image_pil.copy()
    draw = ImageDraw.Draw(out)

    side_len = bx2 - bx1
    img_len = min(w, h)
    ratio = side_len / img_len

    if ratio < 0.15:
        t = 2
        mid_len = 18
    else:
        t = 4
        mid_len = 30

    draw.rectangle((bx1, by1, bx2, by2), outline=GREEN, width=t)

    # Decide side for labels
    body_center_x = (bx1 + bx2) / 2
    image_center_x = w / 2
    labels_on_right = body_center_x < image_center_x

    # Label box sizes
    label_h = 35
    label_w = 260
    gap = 25

    if labels_on_right:
        label_x1 = bx2 + gap
        label_x2 = label_x1 + label_w
        connector_x = bx2
    else:
        label_x2 = bx1 - gap
        label_x1 = label_x2 - label_w
        connector_x = bx1

    top_label_y1 = by1 + 40
    bottom_label_y1 = top_label_y1 + label_h + 15

    # Background rectangles
    draw.rectangle((label_x1, top_label_y1, label_x2, top_label_y1 + label_h), fill=GREEN)
    draw.rectangle((label_x1, bottom_label_y1, label_x2, bottom_label_y1 + label_h), fill=GREEN)

def draw_body_box(image_pil, bbox, face_bbox=None):
    if bbox is None:
        return image_pil

    x1, y1, x2, y2 = bbox
    w, h = image_pil.size

    bx1, by1, bx2, by2 = _make_body_bbox(x1, y1, x2, y2, w, h, pad_ratio=0.10)

    if face_bbox is not None:
        fx1, fy1, fx2, fy2 = face_bbox
        if by1 < fy2:
            by1 = fy2 + 20

    out = image_pil.copy()
    draw = ImageDraw.Draw(out)

    side_len = bx2 - bx1
    img_len = min(w, h)
    ratio = side_len / img_len

    if ratio < 0.15:
        t = 2
        mid_len = 18
    else:
        t = 4
        mid_len = 30

    draw.rectangle((bx1, by1, bx2, by2), outline=GREEN, width=t)

    # where to place labels (left or right)
    body_center_x = (bx1 + bx2) / 2
    image_center_x = w / 2
    labels_on_right = body_center_x < image_center_x

    # label sizes
    base_label_w = 260
    label_h = 35
    gap = 25

    # initial positions
    if labels_on_right:
        label_x1 = bx2 + gap
        label_x2 = label_x1 + base_label_w
        connector_x = bx2
    else:
        label_x2 = bx1 - gap
        label_x1 = label_x2 - base_label_w
        connector_x = bx1

    top_label_y1 = by1 + 40
    bottom_label_y1 = top_label_y1 + label_h + 15

    # FIX 1 — Prevent label box from going outside image
    if label_x1 < 0:
        shift = -label_x1 + 10
        label_x1 += shift
        label_x2 += shift

    if label_x2 > w:
        shift = label_x2 - w + 10
        label_x1 -= shift
        label_x2 -= shift

    # shrink label width if STILL overflowing
    label_w = label_x2 - label_x1
    if label_w < 200:
        label_w = 200

    # recompute end X
    label_x2 = label_x1 + label_w

    # FIX 2 — Text auto-fitting
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    def draw_fitted_text(text, x, y):
        """Shrink text until it fits inside label_w."""
        fsize = 22
        while fsize > 10:
            try:
                font_test = ImageFont.truetype("arial.ttf", fsize)
            except:
                font_test = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font_test)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            if tw <= label_w - 20:  # padding
                draw.text((x + 10, y + (label_h - th) // 2),
                          text, fill=(0, 0, 0), font=font_test)
                return
            fsize -= 1

        # fallback
        draw.text((x + 10, y + 5), text, fill=(0, 0, 0), font=font)

    # Draw background rectangles
    draw.rectangle((label_x1, top_label_y1, label_x2, top_label_y1 + label_h), fill=GREEN)
    draw.rectangle((label_x1, bottom_label_y1, label_x2, bottom_label_y1 + label_h), fill=GREEN)

    # Draw text with auto-fit
    draw_fitted_text("TOP: AI GENERATED TEXT", label_x1, top_label_y1)
    draw_fitted_text("BOTTOM: AI GENERATED TEXT", label_x1, bottom_label_y1)

    # Connector line (bottom label only)
    body_mid_y = (by1 + by2) // 2

    draw.line(
        (connector_x, body_mid_y + 20,
         label_x1, bottom_label_y1 + label_h // 2),
        fill=GREEN, width=t
    )

    return out