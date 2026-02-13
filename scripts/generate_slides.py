"""Step 2: Generate 6-slide TikTok carousels using Google Gemini image generation."""

import json
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

HOOKS_FILE = os.path.join(os.path.dirname(__file__), "..", "hooks.json")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# The "Locked Architecture" base prompt from The_Big_Picture.md / tiktok_master skill
LOCKED_PROMPT = (
    "iPhone photo, shot from above (flat lay) on a dark oak wooden desk. "
    "A white ceramic coffee mug is on the left. An iPhone 15 Pro is centered. "
    "Natural morning light from a window in St. George, Utah. "
    "Slight lens flare. Natural phone camera quality."
)

SLIDE_VARIATIONS = [
    "The iPhone screen shows a faith app with a search bar and the query '{hook}'. A worn leather Bible and a green Quran sit beside the phone.",
    "The iPhone screen shows search results comparing Bible and Quran verses. The coffee mug has steam rising from it.",
    "The iPhone screen shows an AI dialogue between 'Rev. Sarah' and 'Brother Ahmed'. Warm golden light.",
    "The iPhone screen shows a Spanish language toggle activated. A hand reaches for the phone.",
    "The iPhone screen shows a cross-reference chart of shared concepts. Notes and a pen sit nearby.",
    "A person sits back looking at their phone with a serene expression. The desk is softly blurred in the background.",
]


def ensure_output_dir(lang: str) -> Path:
    """Create the date-stamped output directory for slides."""
    today = str(date.today())
    out = Path(ASSETS_DIR) / today / lang
    out.mkdir(parents=True, exist_ok=True)
    return out


def generate_image(prompt: str, output_path: Path) -> bool:
    """Call Gemini 2.5 Flash image generation API. Returns True on success."""
    if not GEMINI_API_KEY:
        print(f"  [SKIP] No GEMINI_API_KEY — writing placeholder to {output_path.name}")
        output_path.write_text(f"PLACEHOLDER IMAGE\nPrompt: {prompt[:200]}")
        return True

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="9:16"),
            ),
        )

        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image.save(str(output_path))
                print(f"  [OK] Generated {output_path.name}")
                return True

        print(f"  [ERR] No image in response for {output_path.name}")
        return False
    except Exception as e:
        print(f"  [ERR] Failed to generate {output_path.name}: {e}")
        return False


def run() -> dict:
    """Execute slide generation for all hooks. Returns summary stats."""
    print(f"[Slides] Starting slide generation for {date.today()}")

    if not os.path.exists(HOOKS_FILE):
        print("[Slides] No hooks.json found — run research.py first")
        return {"generated": 0, "failed": 0}

    with open(HOOKS_FILE) as f:
        data = json.load(f)

    hooks = data.get("hooks", [])
    generated = 0
    failed = 0

    for hook in hooks:
        lang = hook.get("language", "en")
        out_dir = ensure_output_dir(lang)
        hook_text = hook.get("source_trend", "faith exploration")

        for slide_num, variation in enumerate(SLIDE_VARIATIONS, 1):
            prompt = f"{LOCKED_PROMPT} {variation.format(hook=hook_text)}"
            filename = f"hook{hook['id']}_slide{slide_num}.png"
            output_path = out_dir / filename

            if generate_image(prompt, output_path):
                generated += 1
            else:
                failed += 1

    summary = {"generated": generated, "failed": failed}
    print(f"[Slides] Done — {generated} generated, {failed} failed")
    return summary


if __name__ == "__main__":
    run()
