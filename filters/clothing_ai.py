# filters/clothing_ai.py

import os
import io
import json
import base64
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = (
    "You are a fashion assistant. Look at the person in the image and "
    "describe concisely:\n"
    "top: [color] [type]\n"
    "bottom: [color] [type]\n"
    "Respond ONLY as strict JSON like:\n"
    "{\"top\": \"red polo shirt\", \"bottom\": \"light denim shorts\"}"
)


def analyze_clothing_with_gpt(body_crop_pil):
    """
    Takes a PIL Image (body crop) and returns (top_text, bottom_text)
    based on GPT-4o-mini Vision analysis.
    """

    # Encode image to base64 (no temp file needed)
    buf = io.BytesIO()
    body_crop_pil.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
    )

    # Extract text content robustly
    content = response.choices[0].message.content
    if isinstance(content, str):
        raw = content
    else:
        # content is usually a list of parts; join any text fields
        raw = "".join(getattr(part, "text", "") for part in content)

    top = "AI generated top"
    bottom = "AI generated bottom"

    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            if "top" in data:
                top = str.upper((data["top"]))
            if "bottom" in data:
                bottom = str.upper((data["bottom"]))
    except Exception:
        # If JSON parse fails, just fall back to defaults
        pass

    return top, bottom
