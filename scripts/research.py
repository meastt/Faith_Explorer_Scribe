"""Step 1: Research trending theological topics from X/Twitter."""

import os
import time
from datetime import date

import httpx
from dotenv import load_dotenv

load_dotenv()

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "MEMORY.md")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

# Base seed topics — The Scribe refines these based on MEMORY.md learnings
SEED_QUERIES = [
    "interfaith dialogue",
    "Bible vs Quran",
    "theology debate",
    "faith crisis",
    "religious comparison",
    "scripture contradiction",
]


def _read_memory() -> str:
    """Read MEMORY.md for past performance context."""
    if not os.path.exists(MEMORY_FILE):
        return ""
    with open(MEMORY_FILE) as f:
        return f.read()


def _adjust_queries_from_memory(queries: list[str]) -> list[str]:
    """Dynamically add seed queries based on MEMORY.md feedback."""
    memory = _read_memory().lower()
    if not memory:
        return queries

    extra = []
    if "controversial" in memory or "declined" in memory:
        extra.extend([
            "religious controversy today",
            "faith debate viral",
            "scripture hot take",
        ])
    if "spanish" in memory or "español" in memory:
        extra.extend([
            "debate religioso",
            "fe y ciencia",
            "biblia vs corán",
        ])
    if "declined" in memory:
        extra.append("why people leave religion")

    return queries + extra


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


def run() -> list[dict]:
    """Execute the research step. Returns raw trends (no hooks)."""
    print(f"[Research] Starting trend research for {date.today()}")

    queries = _adjust_queries_from_memory(SEED_QUERIES)
    print(f"  [INFO] Searching {len(queries)} queries (base: {len(SEED_QUERIES)}, memory-added: {len(queries) - len(SEED_QUERIES)})")

    all_trends = []
    for query in queries:
        try:
            trends = search_x_trends(query)
            all_trends.extend(trends)
            # X free tier: 1 request per 15 seconds
            if X_BEARER_TOKEN:
                time.sleep(16)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print(f"  [RATE] X rate limit hit — stopping search with {len(all_trends)} trends so far")
                break
            raise

    print(f"[Research] Collected {len(all_trends)} raw trends")
    return all_trends


if __name__ == "__main__":
    trends = run()
    for t in trends[:5]:
        print(f"  - {t['text'][:80]}")
