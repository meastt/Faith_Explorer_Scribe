"""Step 3: Generate 6-slide TikTok carousels using Gemini 3 Pro with baked-in text."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# The "Locked Architecture" base prompt from The_Big_Picture.md / tiktok_master skill
# COMPOSITION: All props (phone, books, mug) are pushed to the LOWER half.
# The UPPER half is intentionally empty — dark wood, soft light, negative space for text.
LOCKED_PROMPT = (
    "iPhone photo, 9:16 vertical portrait, shot from above (flat lay) on a dark oak wooden desk. "
    "COMPOSITION: All objects (phone, books, mug, hands) are arranged in the BOTTOM HALF of the frame only. "
    "The TOP HALF of the image is empty dark wooden desk surface with soft natural morning light "
    "from a window in St. George, Utah — creating a clean, uncluttered area with subtle warm tones. "
    "Slight lens flare. Natural phone camera quality. The empty upper area should feel intentional "
    "and cinematic, like a magazine layout designed for a text headline."
)

SLIDE_SCENE_VARIATIONS = [
    # Slide 1: Hook
    "In the bottom half: An iPhone 15 Pro is centered showing a faith app with a search bar. "
    "A worn leather Bible and a green Quran sit beside the phone. A white ceramic coffee mug on the left.",
    # Slide 2: Setup
    "In the bottom half: An iPhone 15 Pro showing search results comparing Bible and Quran verses. "
    "A white ceramic coffee mug with steam rising sits to the left.",
    # Slide 3: Conflict
    "In the bottom half: An iPhone 15 Pro showing an AI dialogue between 'Rev. Sarah' and 'Brother Ahmed'. "
    "Warm golden light spills across the desk. A coffee mug and worn Bible nearby.",
    # Slide 4: Resolution
    "In the bottom half: An iPhone 15 Pro showing a Spanish language toggle activated. "
    "A hand reaches for the phone. A green Quran and coffee mug sit nearby.",
    # Slide 5: Proof
    "In the bottom half: An iPhone 15 Pro showing a cross-reference chart of shared concepts. "
    "Handwritten notes and a pen sit beside the phone on the dark desk.",
    # Slide 6: CTA
    "In the bottom half: A person's hands resting near a phone on the desk, serene and still. "
    "The desk props are softly blurred. The mood is calm and inviting.",
]


def _build_slide_prompt(slide_num: int, scene: str, text: str, text_style: str) -> str:
    """Build a complete prompt for one slide with baked-in text instructions."""
    return (
        f"{LOCKED_PROMPT} {scene}\n\n"
        f"Text overlay in the UPPER HALF of the image (the empty desk area), "
        f"{text_style}: \"{text}\"\n"
        f"Text style: Bold, punchy, TikTok-viral aesthetic. Large white text with a strong dark "
        f"drop shadow for contrast. Mix font weights — key words BIGGER and bolder, supporting "
        f"words slightly smaller. Slight rotation or stagger on words for energy. "
        f"Think Gen-Z editorial design — clean but with attitude. Sans-serif font. "
        f"Easy to read at phone size even as a thumbnail.\n"
        f"TEXT SAFE ZONE: Place text between 20% and 45% from the top of the image. "
        f"This sits in the empty desk space above the props. "
        f"Do NOT place text in the top 15% (TikTok status bar) or below 50% (where the props are). "
        f"The bottom 40% of the image will be covered by TikTok's UI (caption, buttons)."
    )


def _get_slide_prompts(hook: dict) -> list[str]:
    """Build all 6 slide prompts for a single hook."""
    hook_text = hook.get("hook_text", "Faith Explorer")
    body_texts = hook.get("body_texts", [""] * 4)
    cta_text = hook.get("cta_text", "Explore 144,000+ verses. Link in bio.")

    # Pad body_texts to 4 if short
    while len(body_texts) < 4:
        body_texts.append("")

    prompts = []

    # Slide 1: Hook (large, vertically centered)
    prompts.append(_build_slide_prompt(
        1, SLIDE_SCENE_VARIATIONS[0], hook_text,
        "in the vertical center of the image (around 30-50% from top)"
    ))

    # Slides 2-5: Body texts (vertically centered)
    for i in range(4):
        prompts.append(_build_slide_prompt(
            i + 2, SLIDE_SCENE_VARIATIONS[i + 1], body_texts[i],
            "in the vertical center of the image (around 30-50% from top)"
        ))

    # Slide 6: CTA (vertically centered)
    prompts.append(_build_slide_prompt(
        6, SLIDE_SCENE_VARIATIONS[5], cta_text,
        "in the vertical center of the image (around 35-50% from top)"
    ))

    return prompts


def ensure_output_dir(lang: str) -> Path:
    """Create the date-stamped output directory for slides."""
    today = str(date.today())
    out = Path(ASSETS_DIR) / today / lang
    out.mkdir(parents=True, exist_ok=True)
    return out


def generate_image(prompt: str, output_path: Path) -> bool:
    """Call Gemini 3 Pro image generation. Returns True on success."""
    if not GEMINI_API_KEY:
        print(f"  [SKIP] No GEMINI_API_KEY — creating placeholder PNG for {output_path.name}")
        _create_placeholder_png(prompt, output_path)
        return True

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
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


def _create_placeholder_png(prompt: str, output_path: Path):
    """Create a solid-color PNG with text label for testing without API keys."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # TikTok 9:16 at a reasonable resolution
        img = Image.new("RGB", (1080, 1920), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)

        # Extract the overlay text from the prompt
        text = "PLACEHOLDER"
        if 'Text overlay' in prompt:
            start = prompt.index('"', prompt.index('Text overlay'))
            end = prompt.index('"', start + 1)
            text = prompt[start + 1:end]

        # Draw text (use default font — no external font dependency)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except (OSError, IOError):
            font = ImageFont.load_default()

        # Word wrap
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            if len(test) > 30:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test
        if current_line:
            lines.append(current_line)

        y = 700  # Vertical center (safe zone: 25%-55% of 1920 = 480-1056)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (1080 - w) // 2
            # Shadow
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0), font=font)
            # Text
            draw.text((x, y), line, fill=(255, 255, 255), font=font)
            y += 50

        # Label
        draw.text((20, 20), "PLACEHOLDER — No GEMINI_API_KEY", fill=(100, 100, 100), font=font)

        img.save(str(output_path), "PNG")
    except ImportError:
        # If Pillow not available, write a text file
        output_path.with_suffix(".txt").write_text(f"PLACEHOLDER\nPrompt: {prompt[:300]}")


def run(hooks: list[dict] | None = None) -> dict:
    """Execute slide generation for all hooks.

    Args:
        hooks: List of hook dicts from caption_gen.py, each with:
            id, hook_text, body_texts, cta_text, language

    Returns:
        dict with 'slide_paths' mapping hook_id -> [Path, ...] and summary stats.
    """
    print(f"[Slides] Starting slide generation for {date.today()}")

    if hooks is None:
        print("[Slides] No hooks provided — nothing to generate")
        return {"slide_paths": {}, "generated": 0, "failed": 0}

    generated = 0
    failed = 0
    slide_paths: dict[int, list[str]] = {}

    for hook in hooks:
        hook_id = hook.get("id", 0)
        lang = hook.get("language", "en")
        out_dir = ensure_output_dir(lang)
        prompts = _get_slide_prompts(hook)

        hook_slides = []
        for slide_num, prompt in enumerate(prompts, 1):
            filename = f"hook{hook_id}_slide{slide_num}.png"
            output_path = out_dir / filename

            if generate_image(prompt, output_path):
                hook_slides.append(str(output_path))
                generated += 1
            else:
                failed += 1

        slide_paths[hook_id] = hook_slides

    summary = {"slide_paths": slide_paths, "generated": generated, "failed": failed}
    print(f"[Slides] Done — {generated} generated, {failed} failed")
    return summary


if __name__ == "__main__":
    # Test with sample hooks
    test_hooks = [{
        "id": 1,
        "hook_text": "My roommate said the Bible and Quran have nothing in common.",
        "body_texts": [
            "She challenged me over coffee one morning",
            "I searched 144,000+ verses in seconds",
            "The AI found 47 shared themes",
            "Now she uses it every morning",
        ],
        "cta_text": "Explore 144,000+ verses. Link in bio.",
        "language": "en",
    }]
    result = run(hooks=test_hooks)
    print(f"Result: {result}")
