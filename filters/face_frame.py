from PIL import Image, ImageDraw, ImageOps

GREEN = (0, 255, 0)


def draw_face_box(image_pil, bbox):
    """
    Draw green rectangle around detected face.
    bbox = (x1, y1, x2, y2)
    """
    x1, y1, x2, y2 = bbox
    out = image_pil.copy()
    draw = ImageDraw.Draw(out)
    draw.rectangle((x1, y1, x2, y2), outline=GREEN, width=5)
    return out


def extract_face_crop(image_pil, bbox, padding=0.25):
    """
    Crop face with padding expansion.
    """
    if bbox is None:
        return None

    w, h = image_pil.size
    x1, y1, x2, y2 = bbox

    # padding
    bw = x2 - x1
    bh = y2 - y1
    pad_x = bw * padding
    pad_y = bh * padding

    x1 = max(0, int(x1 - pad_x))
    y1 = max(0, int(y1 - pad_y))
    x2 = min(w, int(x2 + pad_x))
    y2 = min(h, int(y2 + pad_y))

    return image_pil.crop((x1, y1, x2, y2))


def render_face_frame(face_crop, target_width=450):
    """
    Returns a styled green frame containing the face crop.
    """
    if face_crop is None:
        return None

    # Resize crop
    aspect = face_crop.height / face_crop.width
    new_h = int(target_width * aspect)
    face_resized = face_crop.resize((target_width, new_h), Image.LANCZOS)

    padding = 20
    frame_w = target_width + padding * 2
    frame_h = new_h + padding * 2

    frame = Image.new("RGB", (frame_w, frame_h), (0, 0, 0))
    frame.paste(face_resized, (padding, padding))

    draw = ImageDraw.Draw(frame)
    t = 6
    corner = 40

    # Outer border
    draw.rectangle((0, 0, frame_w - 1, frame_h - 1), outline=GREEN, width=t)

    # Corners (HUD style)
    # TL
    draw.line((0, 0, corner, 0), fill=GREEN, width=t)
    draw.line((0, 0, 0, corner), fill=GREEN, width=t)
    # TR
    draw.line((frame_w, 0, frame_w - corner, 0), fill=GREEN, width=t)
    draw.line((frame_w - 1, 0, frame_w - 1, corner), fill=GREEN, width=t)
    # BL
    draw.line((0, frame_h - 1, corner, frame_h - 1), fill=GREEN, width=t)
    draw.line((0, frame_h - 1, 0, frame_h - corner), fill=GREEN, width=t)
    # BR
    draw.line((frame_w - 1, frame_h - 1, frame_w - corner, frame_h - 1), fill=GREEN, width=t)
    draw.line((frame_w - 1, frame_h - 1, frame_w - 1, frame_h - corner), fill=GREEN, width=t)

    return frame
