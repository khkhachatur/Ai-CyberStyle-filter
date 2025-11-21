from PIL import Image, ImageTk
from filters.border_drawer import draw_borders_and_labels

PREVIEW_W = 400
PREVIEW_H = 300

def render_preview(path):
    img = Image.open(path).convert("RGB")
    img.thumbnail((PREVIEW_W, PREVIEW_H))
    img = draw_borders_and_labels(img)
    return ImageTk.PhotoImage(img)
