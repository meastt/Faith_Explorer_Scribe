"""Step 3: Push generated slides to Postiz as TikTok/X drafts."""

import os
from datetime import date
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
POSTIZ_API_KEY = os.getenv("POSTIZ_API_KEY")
POSTIZ_WORKSPACE_ID = os.getenv("POSTIZ_WORKSPACE_ID")
POSTIZ_BASE_URL = "https://app.postiz.com/api/v1"


def upload_media(file_path: Path) -> str | None:
    """Upload a single media file to Postiz. Returns media ID."""
    if not POSTIZ_API_KEY:
        print(f"  [SKIP] No POSTIZ_API_KEY — skipping upload for {file_path.name}")
        return None

    url = f"{POSTIZ_BASE_URL}/media"
    headers = {"Authorization": f"Bearer {POSTIZ_API_KEY}"}

    with open(file_path, "rb") as f:
        resp = httpx.post(
            url,
            headers=headers,
            files={"file": (file_path.name, f, "image/png")},
            data={"workspace_id": POSTIZ_WORKSPACE_ID},
            timeout=30,
        )
    resp.raise_for_status()
    return resp.json().get("id")


def create_draft(title: str, media_ids: list[str], platform: str = "tiktok") -> dict:
    """Create a draft post on Postiz."""
    if not POSTIZ_API_KEY:
        print(f"  [SKIP] No POSTIZ_API_KEY — would create draft: {title}")
        return {"status": "skipped", "title": title}

    url = f"{POSTIZ_BASE_URL}/posts"
    headers = {
        "Authorization": f"Bearer {POSTIZ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "workspace_id": POSTIZ_WORKSPACE_ID,
        "type": "draft",
        "platform": platform,
        "title": title,
        "media": media_ids,
        "visibility": "self",
    }
    resp = httpx.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run() -> list[dict]:
    """Upload today's slides and create drafts. Returns list of results."""
    print(f"[Postiz] Posting drafts for {date.today()}")

    today_dir = Path(ASSETS_DIR) / str(date.today())
    if not today_dir.exists():
        print("[Postiz] No assets found for today — run generate_slides.py first")
        return []

    results = []
    for lang_dir in sorted(today_dir.iterdir()):
        if not lang_dir.is_dir():
            continue

        lang = lang_dir.name
        slide_files = sorted(lang_dir.glob("*.png"))
        if not slide_files:
            # Check for placeholder text files too
            slide_files = sorted(lang_dir.glob("*slide*"))

        # Group slides by hook
        hooks: dict[str, list[Path]] = {}
        for f in slide_files:
            hook_id = f.stem.split("_")[0]  # e.g. "hook1"
            hooks.setdefault(hook_id, []).append(f)

        for hook_id, files in hooks.items():
            title = f"Faith Explorer — {lang.upper()} {hook_id} ({date.today()})"

            media_ids = []
            for file_path in files:
                mid = upload_media(file_path)
                if mid:
                    media_ids.append(mid)

            # Post to both TikTok and X
            for platform in ["tiktok", "twitter"]:
                result = create_draft(title, media_ids, platform)
                results.append(result)

    print(f"[Postiz] Created {len(results)} drafts")
    return results


if __name__ == "__main__":
    run()
