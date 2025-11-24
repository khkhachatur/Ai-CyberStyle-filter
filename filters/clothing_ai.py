import os
import io
import json
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. "
        "Create a .env file in project root:\n\n"
        "OPENAI_API_KEY=sk-xxxxx\n"
    )

client = OpenAI(api_key=api_key)

PROMPT = (
    "You are a fashion assistant. Look at the person in the image and "
    "describe concisely:\n"
    "top: [color] [type]\n"
    "bottom: [color] [type]\n"
    "Respond ONLY as strict JSON like:\n"
    "{\"top\": \"red polo shirt\", \"bottom\": \"light denim shorts\"}"
)

def analyze_clothing_with_gpt(body_crop_pil):
    # Convert crop to base64
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

    raw = response.choices[0].message.content

    top = "AI GENERATED TOP"
    bottom = "AI GENERATED BOTTOM"

    try:
        data = json.loads(raw)
        if "top" in data:
            top = data["top"].upper()
        if "bottom" in data:
            bottom = data["bottom"].upper()
    except:
        pass

    return top, bottom
