import os

def get_unique_save_path(src, suffix="_filtered", ext=".png"):
    base, _ = os.path.splitext(src)
    out = base + suffix + ext
    i = 1
    while os.path.exists(out):
        out = f"{base}{suffix}{i}{ext}"
        i += 1
    return out
