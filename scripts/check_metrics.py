"""Step 5: Pull RevenueCat metrics and log to MEMORY.md with hook details."""

from __future__ import annotations

import os
from datetime import date

import httpx
from dotenv import load_dotenv

load_dotenv()

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "MEMORY.md")
REVENUECAT_API_KEY = os.getenv("REVENUECAT_API_KEY")
REVENUECAT_PROJECT_ID = os.getenv("REVENUECAT_PROJECT_ID")


def fetch_metrics() -> dict:
    """Fetch MRR and download stats from RevenueCat."""
    if not REVENUECAT_API_KEY:
        print("  [SKIP] No REVENUECAT_API_KEY — using placeholder metrics")
        return {
            "mrr": 0.0,
            "active_subscribers": 0,
            "new_trials": 0,
            "downloads": 0,
            "source": "placeholder",
        }

    url = f"https://api.revenuecat.com/v2/projects/{REVENUECAT_PROJECT_ID}/metrics/overview"
    headers = {
        "Authorization": f"Bearer {REVENUECAT_API_KEY}",
        "Content-Type": "application/json",
    }

    resp = httpx.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    return {
        "mrr": data.get("mrr", 0.0),
        "active_subscribers": data.get("active_subscribers", 0),
        "new_trials": data.get("new_trials", 0),
        "downloads": data.get("downloads", 0),
        "source": "revenuecat",
    }


def check_decline(metrics: dict, previous_mrr: float | None = None) -> str | None:
    """Flag if metrics are declining."""
    if previous_mrr is not None and metrics["mrr"] < previous_mrr:
        return f"MRR declined from ${previous_mrr:.2f} to ${metrics['mrr']:.2f} — pivot to more controversial hooks."
    return None


def append_to_memory(entry: str):
    """Append a log entry to MEMORY.md."""
    with open(MEMORY_FILE, "a") as f:
        f.write(f"\n{entry}")


def run(hooks_used: list[dict] | None = None) -> dict:
    """Execute metrics check and log results alongside hooks used today."""
    print(f"[Metrics] Checking RevenueCat metrics for {date.today()}")

    metrics = fetch_metrics()

    entry = (
        f"\n## {date.today()} — Metrics\n"
        f"- MRR: ${metrics['mrr']:.2f}\n"
        f"- Active Subscribers: {metrics['active_subscribers']}\n"
        f"- New Trials: {metrics['new_trials']}\n"
        f"- Downloads: {metrics['downloads']}\n"
        f"- Source: {metrics['source']}\n"
    )

    # Log which hooks were used today (closes the feedback loop)
    if hooks_used:
        entry += "- Hooks posted today:\n"
        for hook in hooks_used:
            lang = hook.get("language", "?")
            text = hook.get("hook_text", "N/A")[:80]
            entry += f"  - [{lang}] {text}\n"

    decline_warning = check_decline(metrics)
    if decline_warning:
        entry += f"- **WARNING:** {decline_warning}\n"
        print(f"  [WARN] {decline_warning}")

    append_to_memory(entry)
    print(f"[Metrics] Logged to MEMORY.md")
    return metrics


if __name__ == "__main__":
    run()
