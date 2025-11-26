from PIL import Image, ImageDraw, ImageFont, ImageOps

GREEN = (0, 255, 0)

def make_face_card(face_image_pil, id_value="UNKNOWN"):

    face_img = face_image_pil.copy()
    face_img = face_img.convert("L")
    face_img = face_img.resize((320, 320))
    face_img = ImageOps.autocontrast(face_img)

    # Original card size
    W, H = 360, 480
    card = Image.new("RGB", (W, H), GREEN)
    draw = ImageDraw.Draw(card)

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 26)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Title
    draw.text((10, 10), "PROFILE", fill=(0,0,0), font=font_title)

    # Face image
    card.paste(face_img, (20, 50))

    # Border around face
    draw.rectangle((20, 50, 340, 370), outline=(0,0,0), width=4)

    # Labels
    draw.text((20, 380), f"ID: {id_value}", fill=(0,0,0), font=font_small)
    draw.text((20, 410), "PROJECT: PICSART", fill=(0,0,0), font=font_small)
    draw.text((20, 440), "STATUS: ACTIVE", fill=(0,0,0), font=font_small)

    scale = 0.8    
    new_W = int(W * scale)
    new_H = int(H * scale)

    card_small = card.resize((new_W, new_H), Image.LANCZOS)

    return card_small
