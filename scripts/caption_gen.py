"""Step 2: Claude-powered hook brainstorming + caption writing."""

from __future__ import annotations

import json
import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "MEMORY.md")
HOOKS_FILE = os.path.join(os.path.dirname(__file__), "..", "hooks.json")
CAPTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "captions.json")

HOOK_SYSTEM_PROMPT = """\
You are The Scribe — a viral TikTok content strategist for Faith Explorer, \
an app that lets users search 144,000+ verses across the Bible and Quran.

Your job: turn trending theological discussions into hooks that stop the scroll.

FORMULA: [Specific Person] + [Relatable Conflict] → AI Solution
- Use specific, relatable people: Abuela, roommate, professor, pastor, imam, coworker
- The conflict must feel personal and real (not preachy, not an ad)
- The resolution involves Faith Explorer's features (search, AI Dialogue Simulator, cross-references)

RULES:
- hook_text MUST be ≤120 characters (it's overlaid on a TikTok slide)
- body_texts: 4 short texts (≤80 chars each) for slides 2-5 explaining the story
- cta_text: call-to-action for slide 6 (≤100 chars)
- Language: generate in the specified language ("en" or "es")
- Human stories, NOT ads. No "download now" energy.
- Each hook must feel like the start of a story someone wants to finish

{memory_context}
"""

CAPTION_SYSTEM_PROMPT = """\
You are The Scribe — writing TikTok captions for Faith Explorer carousel posts.

Write story-style captions that:
- Start with a hook that continues the slide's story
- Feel personal and conversational (not corporate)
- End with 3-5 relevant hashtags
- Total length: 150-300 characters (including hashtags)
- Match the language of the hook ("en" or "es")
"""


def _read_memory() -> str:
    """Read MEMORY.md for past performance context."""
    if not os.path.exists(MEMORY_FILE):
        return ""
    with open(MEMORY_FILE) as f:
        content = f.read()
    if len(content.strip()) <= 50:
        return ""
    return content


def generate_hooks_with_claude(trends: list[dict], count: int = 3) -> list[dict]:
    """Generate creative hooks using Claude, informed by trends and MEMORY.md."""
    memory = _read_memory()
    memory_context = ""
    if memory:
        memory_context = (
            "PAST PERFORMANCE CONTEXT (use this to improve):\n"
            f"```\n{memory[-2000:]}\n```"
        )

    trend_summaries = "\n".join(
        f"- {t['text'][:150]}" for t in trends[:12]
    )

    if not ANTHROPIC_API_KEY:
        print("  [SKIP] No ANTHROPIC_API_KEY — using template fallback hooks")
        return _fallback_hooks(trends, count)

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_prompt = (
        f"Today's trending theological discussions:\n{trend_summaries}\n\n"
        f"Generate exactly {count} hooks. For each hook, output a JSON object with:\n"
        f"- id (integer, starting at 1)\n"
        f"- hook_text (string, ≤120 chars, the overlay for slide 1)\n"
        f"- body_texts (array of 4 strings, ≤80 chars each, for slides 2-5)\n"
        f"- cta_text (string, ≤100 chars, for slide 6)\n"
        f"- language (\"en\" or \"es\" — alternate: first 2 in English, last in Spanish)\n"
        f"- source_trend (string, which trend inspired this)\n\n"
        f"Return ONLY a JSON array of these objects, no markdown fencing."
    )

    resp = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        system=HOOK_SYSTEM_PROMPT.format(memory_context=memory_context),
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = resp.content[0].text.strip()
    # Strip markdown fencing if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    hooks = json.loads(raw)
    print(f"  [OK] Claude generated {len(hooks)} hooks")
    return hooks


def _fallback_hooks(trends: list[dict], count: int) -> list[dict]:
    """Simple template-based fallback when no API key is available."""
    templates = [
        ("My {person} didn't believe {claim}. Faith Explorer showed them the truth.",
         ["She said the Bible and Quran had nothing in common",
          "I searched 144,000+ verses in seconds",
          "The AI found 47 shared themes they never knew about",
          "Now she uses it every morning before coffee"],
         "Explore 144,000+ verses. Link in bio."),
        ("Everyone says {claim}. But search 144,000+ verses and...",
         ["They told me scripture was contradictory",
          "So I asked the AI Dialogue Simulator",
          "Rev. Sarah and Brother Ahmed debated it live",
          "The cross-references changed everything"],
         "See what 144,000+ verses reveal. Link in bio."),
        ("{person} me desafió sobre {claim}. La IA lo resolvió.",
         ["Dijo que la fe era solo tradición",
          "Busqué en 144,000+ versículos en español",
          "El Simulador de Diálogo lo explicó todo",
          "Ahora exploramos juntos cada semana"],
         "Explora 144,000+ versículos. Link en bio."),
    ]

    persons = ["roommate", "professor", "Mi abuela"]
    claims = ["faith is outdated", "scriptures contradict each other", "la fe no tiene lógica"]

    hooks = []
    for i in range(min(count, len(templates))):
        tmpl, body, cta = templates[i]
        hook_text = tmpl.format(person=persons[i], claim=claims[i])
        trend_text = trends[i]["text"][:120] if i < len(trends) else "general"
        hooks.append({
            "id": i + 1,
            "hook_text": hook_text[:120],
            "body_texts": body,
            "cta_text": cta,
            "language": "es" if i == 2 else "en",
            "source_trend": trend_text,
        })
    return hooks


def generate_captions(hooks: list[dict]) -> list[dict]:
    """Generate story-style TikTok captions for each hook."""
    if not ANTHROPIC_API_KEY:
        print("  [SKIP] No ANTHROPIC_API_KEY — using template fallback captions")
        return _fallback_captions(hooks)

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    hooks_desc = json.dumps(hooks, indent=2)
    user_prompt = (
        f"Here are the hooks for today's TikTok carousels:\n{hooks_desc}\n\n"
        f"For each hook, write a story-style TikTok caption (150-300 chars including "
        f"3-5 hashtags). Match the hook's language.\n\n"
        f"Return ONLY a JSON array where each object has:\n"
        f"- hook_id (integer, matching the hook's id)\n"
        f"- caption (string, the full caption with hashtags)\n"
        f"No markdown fencing."
    )

    resp = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        system=CAPTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    captions = json.loads(raw)
    print(f"  [OK] Claude generated {len(captions)} captions")
    return captions


def _fallback_captions(hooks: list[dict]) -> list[dict]:
    """Template captions when no API key is available."""
    en_template = (
        "I never expected this to change how I see scripture... "
        "but here we are. 🤯 #FaithExplorer #Bible #Quran #InterfaithDialogue"
    )
    es_template = (
        "Nunca pensé que esto cambiaría cómo veo las escrituras... "
        "pero aquí estamos. 🤯 #FaithExplorer #Fe #Biblia #DiálogoInterreligioso"
    )
    captions = []
    for hook in hooks:
        lang = hook.get("language", "en")
        captions.append({
            "hook_id": hook["id"],
            "caption": es_template if lang == "es" else en_template,
        })
    return captions


def run(trends: list[dict]) -> dict:
    """Orchestrator: generate hooks + captions from raw trends.

    Returns dict with 'hooks' and 'captions' keys.
    Also writes hooks.json and captions.json for inspection.
    """
    print(f"[CaptionGen] Generating hooks and captions for {date.today()}")

    hooks = generate_hooks_with_claude(trends, count=3)
    captions = generate_captions(hooks)

    # Write to disk for inspection/debugging
    with open(HOOKS_FILE, "w") as f:
        json.dump({"date": str(date.today()), "hooks": hooks}, f, indent=2)
    print(f"  [OK] Wrote {len(hooks)} hooks -> hooks.json")

    with open(CAPTIONS_FILE, "w") as f:
        json.dump({"date": str(date.today()), "captions": captions}, f, indent=2)
    print(f"  [OK] Wrote {len(captions)} captions -> captions.json")

    return {"hooks": hooks, "captions": captions}


if __name__ == "__main__":
    # For standalone testing, use placeholder trends
    test_trends = [
        {"text": "Why do the Bible and Quran tell the same stories differently?", "source": "test"},
        {"text": "My professor said all religions are the same. Is that true?", "source": "test"},
        {"text": "Debate sobre fe y ciencia en las universidades", "source": "test"},
    ]
    result = run(test_trends)
    print(json.dumps(result, indent=2, ensure_ascii=False))
