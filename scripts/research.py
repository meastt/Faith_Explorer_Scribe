"""Step 1: Research trending theological topics and generate hook ideas."""

import json
import os
from datetime import date

import httpx
from dotenv import load_dotenv

load_dotenv()

HOOKS_FILE = os.path.join(os.path.dirname(__file__), "..", "hooks.json")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Sample seed topics — The Scribe refines these based on MEMORY.md learnings
SEED_QUERIES = [
    "interfaith dialogue",
    "Bible vs Quran",
    "theology debate",
    "faith crisis",
    "religious comparison",
    "scripture contradiction",
]


def search_x_trends(query: str) -> list[dict]:
    """Search X/Twitter for trending theological discussions."""
    if not X_BEARER_TOKEN:
        print(f"  [SKIP] No X_BEARER_TOKEN set — using placeholder for '{query}'")
        return [{"text": f"Placeholder trend for: {query}", "source": "placeholder"}]

    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
    params = {"query": f"{query} lang:en -is:retweet", "max_results": 10}

    resp = httpx.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return [{"text": t["text"], "source": "x"} for t in data]


def generate_hooks(trends: list[dict]) -> list[dict]:
    """Turn raw trends into hook ideas using the Skeptic-to-Believer formula."""
    hooks = []
    hook_templates = [
        "My {person} didn't believe {claim}. I used Faith Explorer to show them the truth.",
        "Everyone says {claim}. But when you actually search 144,000+ verses...",
        "{person} challenged me on {claim}. The AI Dialogue Simulator settled it.",
    ]
    for i, trend in enumerate(trends[:6]):
        template = hook_templates[i % len(hook_templates)]
        hooks.append({
            "id": i + 1,
            "template": template,
            "source_trend": trend["text"][:120],
            "language": "en" if i % 2 == 0 else "es",
        })
    return hooks


def run() -> list[dict]:
    """Execute the research step. Returns hook ideas and writes hooks.json."""
    print(f"[Research] Starting trend research for {date.today()}")

    all_trends = []
    for query in SEED_QUERIES:
        trends = search_x_trends(query)
        all_trends.extend(trends)

    hooks = generate_hooks(all_trends)

    with open(HOOKS_FILE, "w") as f:
        json.dump({"date": str(date.today()), "hooks": hooks}, f, indent=2)

    print(f"[Research] Generated {len(hooks)} hooks -> hooks.json")
    return hooks


if __name__ == "__main__":
    run()
