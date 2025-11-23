from PIL import Image, ImageDraw, ImageOps

GREEN = (0, 255, 0)

def _make_square_bbox(x1, y1, x2, y2, image_w, image_h, pad_ratio=0.15):
    """
    Converts a bounding box to a square, centered on the original,
    and adds a padding margin of pad_ratio.
    """
    bw = x2 - x1
    bh = y2 - y1
    side = max(bw, bh)
    half = side / 2.0
    cx = x1 + bw / 2.0
    cy = y1 + bh / 2.0

    # Add padding
    half += side * pad_ratio

    nx1 = cx - half
    ny1 = cy - half
    nx2 = cx + half
    ny2 = cy + half

    # Clamp within image bounds
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

    t = 6          
    corner = 40    
    mid_len = 30  

    # Outer box
    draw.rectangle((sx1, sy1, sx2, sy2), outline=GREEN, width=t)

    cx = (sx1 + sx2) // 2    
    
    cy = (sy1 + sy2) // 2    
    
    # Center ticks
    
    # draw.line((cx, sy1, cx, sy1 + mid_len), fill=GREEN, width=t)          
    draw.line((sx1, cy, sx1 + mid_len, cy), fill=GREEN, width=t)          
    draw.line((sx2 - mid_len, cy, sx2, cy), fill=GREEN, width=t)          
    # draw.line((cx, sy2, cx, sy2 - mid_len), fill=GREEN, width=t)          

    # DOUBLE HEADER (Top)

    header_height = t * 2          
    bar_length = (sx2 - sx1) * 0.55 

    # First top bar (outer)
    draw.line(
        (cx - bar_length//2, sy1 - header_height,
         cx + bar_length//2, sy1 - header_height),
        fill=GREEN, width=t
    )

    # Second top bar (inner)
    draw.line(
        (cx - bar_length//2 + 20, sy1 - header_height - (t * 2),
         cx + bar_length//2 - 20, sy1 - header_height - (t * 2)),
        fill=GREEN, width=t
    )

    return out



def extract_face_crop(image_pil, bbox, padding=0.3):
    """
    Crop the face region, making it square and adding padding.
    """
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

    # Resize crop – keep aspect ratio (should be square or near-square)
    aspect = face_crop.height / face_crop.width
    new_h = int(target_width * aspect)
    face_resized = face_crop.resize((target_width, new_h), Image.LANCZOS)

    padding = 20
    frame_w = target_width + padding * 2
    frame_h = new_h + padding * 2

    cx = frame_w // 2               # center x
    mid = 50  

    frame = Image.new("RGB", (frame_w, frame_h), (0, 0, 0))
    frame.paste(face_resized, (padding, padding))

    draw = ImageDraw.Draw(frame)
    t = 15
    corner = 40

    # Outer border
   


    return frame
