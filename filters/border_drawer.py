from PIL import Image, ImageDraw, ImageFont

def draw_borders_and_labels(img):
    out = img.copy()
    draw = ImageDraw.Draw(out)

    # Text size helper for Pillow 10+
    def text_size(draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    w, h = out.size
    margin_x = w * 0.03
    margin_y = h * 0.03
    thick = 2 if min(w, h) >= 600 else 1
    color = (255, 255, 255)

    def I(x): return (int(x[0]), int(x[1]))

    # ----------------------------------------
    # BORDER LENGTHS (proportional)
    # ----------------------------------------
    TLW = w * 0.20
    TLH = h * 0.20
    TRW = w * 0.20
    TRH = h * 0.20
    BLW = w * 0.25
    BLH = h * 0.18
    
    BRH = h * 0.18

    # ----------------------------------------
    # 1) TOP LEFT
    # ----------------------------------------
    draw.line(I((margin_x, margin_y)) + I((margin_x + TLW, margin_y)), fill=color, width=thick)
    draw.line(I((margin_x, margin_y)) + I((margin_x, margin_y + TLH)), fill=color, width=thick)

    # ----------------------------------------
    # 2) TOP RIGHT
    # ----------------------------------------
    tx = w - margin_x
    ty = margin_y
    draw.line(I((tx, ty)) + I((tx - TRW, ty)), fill=color, width=thick)
    draw.line(I((tx, ty)) + I((tx, ty + TRH)), fill=color, width=thick)

    # ----------------------------------------
    # 3) BOTTOM LEFT
    # ----------------------------------------
    bx = margin_x
    by = h - margin_y
    draw.line(I((bx, by)) + I((bx + BLW, by)), fill=color, width=thick)
    draw.line(I((bx, by)) + I((bx, by - BLH)), fill=color, width=thick)

    # ----------------------------------------
    # 4) BOTTOM RIGHT
    # ----------------------------------------
    brx = w - margin_x
    bry = h - margin_y
    draw.line(I((brx, bry)) + I((brx - TRW, bry)), fill=color, width=thick)
    draw.line(I((brx, bry)) + I((brx, bry - BRH)), fill=color, width=thick)

    # ----------------------------------------
    # FONT
    # ----------------------------------------
    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", int(min(w, h) * 0.024))
    except:
        font = ImageFont.load_default()

    pad = int(min(w, h) * 0.012)

    # ----------------------------------------
    # TOP LEFT TEXT (INSIDE)
    # ----------------------------------------
    date_text = "2025-04-10"

    draw.text(
        I((margin_x + pad, margin_y + pad)),
        date_text,
        fill=color,
        font=font
    )

    # ----------------------------------------
    # TOP RIGHT (EMPTY INSIDE)
    # ----------------------------------------
    # No text here by your request

    # ----------------------------------------
    # TOP BATTERY (CENTERED, OUTSIDE)
    # ----------------------------------------
    percent_text = "69%"
    pw, ph = text_size(draw, percent_text, font)

    left_end = margin_x + TLW
    right_end = (w - margin_x) - TRW
    mid_x = (left_end + right_end) / 2

    battery_y = margin_y - ph/2   # aligns with border height
    draw.text(I((mid_x - pw/2, battery_y)), percent_text, fill=color, font=font)

    # ----------------------------------------
    # BOTTOM LEFT (INSIDE)
    # ----------------------------------------
    bl_label = "PICSART X KHACH"
    lw, lh = text_size(draw, bl_label, font)

    bl_y = (h - margin_y) - lh - pad  # LOWER inside position

    draw.text(
        I((margin_x + pad, bl_y)),
        bl_label,
        fill=color,
        font=font
    )

    # ----------------------------------------
    # BOTTOM CENTER (CENTERED)
    # ----------------------------------------
    label1 = "2025"
    label2 = "PAX"

    l1w, l1h = text_size(draw, label1, font)
    l2w, l2h = text_size(draw, label2, font)

    total_w = l1w + pad + l2w
    cx = w / 2 - total_w / 2

    bottom_y = (h - margin_y) - l1h / 2   # <<< ALIGN WITH BORDER

    draw.text(I((cx, bottom_y)), label1, fill=color, font=font)
    draw.text(I((cx + l1w + pad, bottom_y)), label2, fill=color, font=font)
    return out
