from PIL import Image, ImageDraw, ImageOps

GREEN = (0, 255, 0)

def _make_square_bbox(x1, y1, x2, y2, image_w, image_h, pad_ratio=0.15):
    bw = x2 - x1
    bh = y2 - y1
    side = max(bw, bh)
    half = side / 2.0
    cx = x1 + bw / 2.0
    cy = y1 + bh / 2.0

    half += side * pad_ratio

    nx1 = cx - half
    ny1 = cy - half
    nx2 = cx + half
    ny2 = cy + half

    if nx1 < 0:
        nx1 = 0
        nx2 = min(image_w, 2 * half)
    if ny1 < 0:
        ny1 = 0
        ny2 = min(image_h, 2 * half)
    if nx2 > image_w:
        nx2 = image_w
        nx1 = max(0, image_w - 2 * half)
    if ny2 > image_h:
        ny2 = image_h
        ny1 = max(0, image_h - 2 * half)

    return int(nx1), int(ny1), int(nx2), int(ny2)


def draw_face_box(image_pil, bbox):
    """
    Draw a HUD-styled green square face box on the main image.
    """
    x1, y1, x2, y2 = bbox
    w, h = image_pil.size

    sx1, sy1, sx2, sy2 = _make_square_bbox(x1, y1, x2, y2, w, h, pad_ratio=0.30)

    out = image_pil.copy()
    draw = ImageDraw.Draw(out)

    # -------------------------------------------------------
    # Thickness auto-adjusting based on face size in image
    # -------------------------------------------------------
    face_w = sx2 - sx1
    face_h = sy2 - sy1
    face_area = face_w * face_h
    img_area = w * h
    ratio = face_area / img_area
    mid_len = 30
    corner = 40

    if ratio < 0.03:
        t = 3   # thin lines - face far
    elif ratio < 0.08:
        t = 5   # medium
    else:
        t = 7   
        
    if ratio < 0.03:        # very far face
        mid_len = 7
    elif ratio < 0.08:      # medium distance
        mid_len = 20
    else:                   # close face
        mid_len = 30


    # Outer box
    draw.rectangle((sx1, sy1, sx2, sy2), outline=GREEN, width=t)

    cx = (sx1 + sx2) // 2
    cy = (sy1 + sy2) // 2

    # Center ticks
    draw.line((sx1, cy, sx1 + mid_len, cy), fill=GREEN, width=t)
    draw.line((sx2 - mid_len, cy, sx2, cy), fill=GREEN, width=t)

    # DOUBLE HEADER (Top)
    header_height = t * 2
    bar_length = (sx2 - sx1) * 0.55

    draw.line(
        (cx - bar_length//2, sy1 - header_height,
         cx + bar_length//2, sy1 - header_height),
        fill=GREEN, width=t
    )

    draw.line(
        (cx - bar_length//2 + 20, sy1 - header_height - (t * 2),
         cx + bar_length//2 - 20, sy1 - header_height - (t * 2)),
        fill=GREEN, width=t
    )

    return out


def extract_face_crop(image_pil, bbox, padding=0.3):
    if bbox is None:
        return None

    w, h = image_pil.size
    x1, y1, x2, y2 = bbox
    sx1, sy1, sx2, sy2 = _make_square_bbox(x1, y1, x2, y2, w, h, pad_ratio=padding)
    return image_pil.crop((sx1, sy1, sx2, sy2))


def render_face_frame(face_crop, target_width=450):
    """
    Returns a styled green HUD frame containing the face crop (square).
    """
    if face_crop is None:
        return None

    aspect = face_crop.height / face_crop.width
    new_h = int(target_width * aspect)
    face_resized = face_crop.resize((target_width, new_h), Image.LANCZOS)

    padding = 20
    frame_w = target_width + padding * 2
    frame_h = new_h + padding * 2

    # -------------------------------------------------------
    # Thickness auto-adjust based on face crop size
    # -------------------------------------------------------
    ratio = (target_width * new_h) / (frame_w * frame_h)

  

    frame = Image.new("RGB", (frame_w, frame_h), (0, 0, 0))
    frame.paste(face_resized, (padding, padding))

    return frame
