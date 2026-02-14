"""Orchestrator: Runs the full daily pipeline in sequence with data passing."""

import json
import os
import sys
import traceback
from datetime import date

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "MEMORY.md")
HOOKS_FILE = os.path.join(os.path.dirname(__file__), "..", "hooks.json")


def log_to_memory(message: str):
    with open(MEMORY_FILE, "a") as f:
        f.write(f"\n{message}")


def run_pipeline():
    print(f"{'='*50}")
    print(f"  Faith Explorer Scribe — Daily Pipeline")
    print(f"  {date.today()}")
    print(f"{'='*50}\n")

    import research
    import caption_gen
    import generate_slides
    import post_to_postiz
    import check_metrics

    results = {}

    # Step 1: Research — raw trends from X
    print("\n--- Step 1: Research ---")
    try:
        trends = research.run()
        results["Research"] = {"status": "ok", "trend_count": len(trends)}
        print(f"[OK] Research completed — {len(trends)} trends")
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        results["Research"] = {"status": "error", "error": error_msg}
        print(f"[ERR] Research failed: {error_msg}")
        traceback.print_exc()
        log_to_memory(f"\n### {date.today()} — Pipeline Error\n- Step: Research\n- Error: {error_msg}\n")
        trends = []

    # Step 2: Caption Gen — hooks + captions via Claude
    print("\n--- Step 2: Caption Generation ---")
    gen = {"hooks": [], "captions": []}
    try:
        gen = caption_gen.run(trends)
        results["CaptionGen"] = {"status": "ok", "hooks": len(gen["hooks"]), "captions": len(gen["captions"])}
        print(f"[OK] CaptionGen completed — {len(gen['hooks'])} hooks, {len(gen['captions'])} captions")
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        results["CaptionGen"] = {"status": "error", "error": error_msg}
        print(f"[ERR] CaptionGen failed: {error_msg}")
        traceback.print_exc()
        log_to_memory(f"\n### {date.today()} — Pipeline Error\n- Step: CaptionGen\n- Error: {error_msg}\n")

    # Step 3: Generate Slides — Gemini 3 Pro images with baked-in text
    print("\n--- Step 3: Generate Slides ---")
    slides = {"slide_paths": {}}
    try:
        slides = generate_slides.run(hooks=gen["hooks"])
        results["Slides"] = {"status": "ok", "generated": slides.get("generated", 0), "failed": slides.get("failed", 0)}
        print(f"[OK] Slides completed — {slides.get('generated', 0)} generated")
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        results["Slides"] = {"status": "error", "error": error_msg}
        print(f"[ERR] Slides failed: {error_msg}")
        traceback.print_exc()
        log_to_memory(f"\n### {date.today()} — Pipeline Error\n- Step: Slides\n- Error: {error_msg}\n")

    # Step 4: Post to Postiz — upload drafts
    print("\n--- Step 4: Post to Postiz ---")
    try:
        post_results = post_to_postiz.run(
            captions=gen["captions"],
            slide_paths=slides["slide_paths"],
        )
        results["Postiz"] = {"status": "ok", "drafts": len(post_results)}
        print(f"[OK] Postiz completed — {len(post_results)} drafts")
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        results["Postiz"] = {"status": "error", "error": error_msg}
        print(f"[ERR] Postiz failed: {error_msg}")
        traceback.print_exc()
        log_to_memory(f"\n### {date.today()} — Pipeline Error\n- Step: Postiz\n- Error: {error_msg}\n")

    # Step 5: Check Metrics — RevenueCat + MEMORY.md logging
    print("\n--- Step 5: Check Metrics ---")
    try:
        metrics = check_metrics.run(hooks_used=gen["hooks"])
        results["Metrics"] = {"status": "ok", "metrics": metrics}
        print(f"[OK] Metrics completed")
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        results["Metrics"] = {"status": "error", "error": error_msg}
        print(f"[ERR] Metrics failed: {error_msg}")
        traceback.print_exc()
        log_to_memory(f"\n### {date.today()} — Pipeline Error\n- Step: Metrics\n- Error: {error_msg}\n")

    # Summary
    ok_count = sum(1 for r in results.values() if r["status"] == "ok")
    err_count = sum(1 for r in results.values() if r["status"] == "error")

    summary = (
        f"\n## {date.today()} — Pipeline Run\n"
        f"- Steps OK: {ok_count}/5\n"
        f"- Steps Failed: {err_count}/5\n"
    )

    # Log hook summaries for the feedback loop
    if gen["hooks"]:
        summary += "- Hooks used:\n"
        for hook in gen["hooks"]:
            summary += f"  - [{hook.get('language', '?')}] {hook.get('hook_text', 'N/A')[:80]}\n"

    log_to_memory(summary)

    print(f"\n{'='*50}")
    print(f"  Pipeline complete: {ok_count} ok, {err_count} errors")
    print(f"{'='*50}")

    return results


if __name__ == "__main__":
    run_pipeline()
