from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import math

def cool_green_tint(img, strength=0.22):
    overlay = Image.new("RGB", img.size, (20, 110, 120))
    return Image.blend(img, overlay, strength)

def add_noise(img, amount=0.06):
    noise = Image.effect_noise(img.size, 100).convert("L")
    noise_rgb = Image.merge("RGB", [noise]*3)
    return Image.blend(img, noise_rgb, amount)

def make_vignette_mask(size, strength=0.85):
    w, h = size
    cx, cy = w/2, h/2
    max_d = math.hypot(cx, cy)

    mask = Image.new("L", (w, h))
    px = mask.load()

    for y in range(h):
        for x in range(w):
            t = math.hypot(x-cx, y-cy) / max_d
            px[x, y] = int(255 * (t ** 1.5) * strength)

    return mask

def apply_stylistic_pipeline(img):
    img = img.convert("RGB")

    from .stylistic_filters import cool_green_tint, add_noise, make_vignette_mask

    img = cool_green_tint(img, 0.22)

    mask = make_vignette_mask(img.size, 0.85)
    dark = Image.new("RGB", img.size, (0,0,0))
    img = Image.composite(Image.blend(img, dark, 0.45), img, ImageOps.invert(mask))

    img = add_noise(img)
    img = ImageEnhance.Contrast(img).enhance(1.18)

    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=140, threshold=3))

    return img
