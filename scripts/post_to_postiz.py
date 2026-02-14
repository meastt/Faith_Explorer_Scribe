"""Step 4: Push generated slides to Postiz as TikTok/X drafts."""

from __future__ import annotations

import os
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

POSTIZ_API_KEY = os.getenv("POSTIZ_API_KEY")
POSTIZ_BASE_URL = "https://api.postiz.com/public/v1"


def get_integrations() -> list[dict]:
    """Fetch connected social accounts from Postiz.

    Response items have 'id' and 'identifier' (e.g. "x", "tiktok", "instagram").
    """
    if not POSTIZ_API_KEY:
        print("  [SKIP] No POSTIZ_API_KEY — returning placeholder integrations")
        return [
            {"id": "placeholder-tiktok", "identifier": "tiktok", "name": "TikTok (placeholder)"},
            {"id": "placeholder-x", "identifier": "x", "name": "X (placeholder)"},
        ]

    url = f"{POSTIZ_BASE_URL}/integrations"
    headers = {"Authorization": POSTIZ_API_KEY}

    resp = httpx.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def upload_media(file_path: Path, max_retries: int = 3) -> dict | None:
    """Upload a single media file to Postiz. Returns {id, path} dict.

    Retries on 429 rate limit with exponential backoff.
    """
    if not POSTIZ_API_KEY:
        print(f"  [SKIP] No POSTIZ_API_KEY — skipping upload for {file_path.name}")
        return None

    url = f"{POSTIZ_BASE_URL}/upload"
    headers = {"Authorization": POSTIZ_API_KEY}

    for attempt in range(max_retries):
        with open(file_path, "rb") as f:
            resp = httpx.post(
                url,
                headers=headers,
                files={"file": (file_path.name, f, "image/png")},
                timeout=60,
            )
        if resp.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"  [RATE] Postiz rate limit — waiting {wait}s before retry ({attempt + 1}/{max_retries})")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        return {"id": data["id"], "path": data.get("path", "")}

    print(f"  [ERR] Upload failed after {max_retries} retries for {file_path.name}")
    return None


def _platform_settings(platform: str) -> dict:
    """Return required platform-specific settings for Postiz."""
    if platform == "x":
        return {"who_can_reply_post": "everyone"}
    if platform == "tiktok":
        return {
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "duet": False,
            "stitch": False,
            "comment": True,
            "autoAddMusic": "no",
            "brand_content_toggle": False,
            "brand_organic_toggle": False,
            "content_posting_method": "DIRECT_POST",
        }
    return {}


# Peak TikTok engagement times in MST (UTC-7), expressed as UTC hours
# Morning 10am MST = 17:00 UTC, Afternoon 2pm MST = 21:00 UTC, Evening 6pm MST = 01:00 UTC+1
POSTING_SLOTS_UTC = [17, 21, 1]


def create_draft(caption: str, media: list[dict], integration_id: str, platform: str = "tiktok", schedule_date: str | None = None) -> dict:
    """Create a scheduled post on Postiz.

    Args:
        caption: Post caption text
        media: List of {id, path} dicts from upload_media()
        integration_id: ID of the connected social account
        platform: Platform identifier (e.g. "tiktok")
        schedule_date: ISO 8601 date string. If None, defaults to tomorrow 2pm UTC.
    """
    if not POSTIZ_API_KEY:
        print(f"  [SKIP] No POSTIZ_API_KEY — would create draft: {caption[:60]}...")
        return {"status": "skipped", "caption": caption[:60], "platform": platform}

    url = f"{POSTIZ_BASE_URL}/posts"
    headers = {
        "Authorization": POSTIZ_API_KEY,
        "Content-Type": "application/json",
    }

    if schedule_date is None:
        schedule_date = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
            hour=14, minute=0, second=0, microsecond=0
        ).isoformat()

    payload = {
        "type": "draft",
        "date": schedule_date,
        "shortLink": False,
        "tags": [],
        "posts": [
            {
                "integration": {"id": integration_id},
                "value": [
                    {
                        "content": caption,
                        "image": media,
                    }
                ],
                "settings": _platform_settings(platform),
            }
        ],
    }

    resp = httpx.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run(captions: list[dict] | None = None, slide_paths: dict | None = None) -> list[dict]:
    """Upload slides and create drafts for each hook.

    Args:
        captions: List of dicts with 'hook_id' and 'caption' from caption_gen.py
        slide_paths: Dict mapping hook_id -> [file_path, ...] from generate_slides.py
    """
    print(f"[Postiz] Posting drafts for {date.today()}")

    if not captions or not slide_paths:
        print("[Postiz] No captions or slide_paths provided — nothing to post")
        return []

    # Get connected integrations — keyed by 'identifier' (e.g. "x", "tiktok")
    integrations = get_integrations()
    integration_map: dict[str, str] = {}
    for integ in integrations:
        identifier = integ.get("identifier", "unknown")
        integration_map[identifier] = integ["id"]

    # Build staggered schedule: first post soon, rest spread across slots
    now = datetime.now(timezone.utc)
    schedule_times = []
    for i in range(len(captions)):
        slot_hour = POSTING_SLOTS_UTC[i % len(POSTING_SLOTS_UTC)]
        # First post: today if there's a slot left, otherwise tomorrow
        days_offset = i // len(POSTING_SLOTS_UTC)
        candidate = (now + timedelta(days=days_offset)).replace(
            hour=slot_hour, minute=0, second=0, microsecond=0
        )
        # If slot_hour < current hour (e.g. 1:00 UTC for evening MST), push to next day
        if slot_hour < 2:
            candidate += timedelta(days=1)
        # If candidate is in the past, push to tomorrow
        if candidate <= now + timedelta(minutes=10):
            candidate += timedelta(days=1)
        schedule_times.append(candidate.isoformat())

    results = []
    for idx, caption_entry in enumerate(captions):
        hook_id = caption_entry.get("hook_id")
        caption = caption_entry.get("caption", "")
        hook_slides = slide_paths.get(hook_id, [])

        if not hook_slides:
            print(f"  [SKIP] No slides for hook {hook_id}")
            continue

        # Upload media
        media = []
        for slide_path in hook_slides:
            path = Path(slide_path)
            if path.exists() and path.suffix == ".png":
                uploaded = upload_media(path)
                if uploaded:
                    media.append(uploaded)

        sched = schedule_times[idx] if idx < len(schedule_times) else None
        print(f"  [SCHED] Hook {hook_id} -> {sched}")

        # Post to TikTok only (X integration is for trend research, not posting)
        for platform in ["tiktok"]:
            integration_id = integration_map.get(platform, "")
            if not integration_id and POSTIZ_API_KEY:
                print(f"  [WARN] No '{platform}' integration found — skipping")
                continue

            try:
                result = create_draft(caption, media, integration_id, platform, schedule_date=sched)
                results.append(result)
            except Exception as e:
                print(f"  [ERR] Failed to create {platform} draft for hook {hook_id}: {e}")
                results.append({"status": "error", "platform": platform, "error": str(e)})

    print(f"[Postiz] Created {len(results)} drafts")
    return results


if __name__ == "__main__":
    run()
