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
    """
    Make a padded **rectangular** bbox for full body (no squaring).
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
    
    label_h = 35
    label_w = 260

    # Gap from body box
    gap = 25

    # Position for label boxes (to the right of the body frame)
    label_x1 = bx2 + gap
    label_x2 = label_x1 + label_w

    # Y positions
    top_label_y1 = by1 + 40
    bottom_label_y1 = top_label_y1 + label_h + 15

    # Backgrounds (green)
    draw.rectangle((label_x1, top_label_y1, label_x2, top_label_y1 + label_h), fill=GREEN)
    draw.rectangle((label_x1, bottom_label_y1, label_x2, bottom_label_y1 + label_h), fill=GREEN)

    # Text (black)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # ➕ AI-generated placeholders
    top_text = "TOP: AI GENERATED TEXT"
    bottom_text = "BOTTOM: AI GENERATED TEXT"

    draw.text((label_x1 + 10, top_label_y1 + 8), top_text, fill=(0, 0, 0), font=font)
    draw.text((label_x1 + 10, bottom_label_y1 + 8), bottom_text, fill=(0, 0, 0), font=font)

    # ➕ connector lines
    body_mid_y = (by1 + by2) // 2

    # Line from body → TOP label
    draw.line(
        (bx2, body_mid_y - 20, label_x1, top_label_y1 + label_h // 2),
        fill=GREEN, width=t
    )

    # Line from body → BOTTOM label
    draw.line(
        (bx2, body_mid_y + 20, label_x1, bottom_label_y1 + label_h // 2),
        fill=GREEN, width=t
    )

    return out
