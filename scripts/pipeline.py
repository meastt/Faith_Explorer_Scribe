"""Orchestrator: Runs the full daily pipeline (Steps 1-4) in sequence."""

import os
import sys
import traceback
from datetime import date

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "MEMORY.md")


def log_to_memory(message: str):
    with open(MEMORY_FILE, "a") as f:
        f.write(f"\n{message}")


def run_pipeline():
    print(f"{'='*50}")
    print(f"  Faith Explorer Scribe — Daily Pipeline")
    print(f"  {date.today()}")
    print(f"{'='*50}\n")

    steps = [
        ("Research", "research", "run"),
        ("Generate Slides", "generate_slides", "run"),
        ("Post to Postiz", "post_to_postiz", "run"),
        ("Check Metrics", "check_metrics", "run"),
    ]

    results = {}
    for step_name, module_name, func_name in steps:
        print(f"\n--- Step: {step_name} ---")
        try:
            module = __import__(module_name)
            func = getattr(module, func_name)
            result = func()
            results[step_name] = {"status": "ok", "result": result}
            print(f"[OK] {step_name} completed")
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            results[step_name] = {"status": "error", "error": error_msg}
            print(f"[ERR] {step_name} failed: {error_msg}")
            traceback.print_exc()
            log_to_memory(
                f"\n### {date.today()} — Pipeline Error\n"
                f"- Step: {step_name}\n"
                f"- Error: {error_msg}\n"
            )

    # Summary
    ok_count = sum(1 for r in results.values() if r["status"] == "ok")
    err_count = sum(1 for r in results.values() if r["status"] == "error")

    summary = (
        f"\n## {date.today()} — Pipeline Run\n"
        f"- Steps OK: {ok_count}/{len(steps)}\n"
        f"- Steps Failed: {err_count}/{len(steps)}\n"
    )
    log_to_memory(summary)

    print(f"\n{'='*50}")
    print(f"  Pipeline complete: {ok_count} ok, {err_count} errors")
    print(f"{'='*50}")

    return results


if __name__ == "__main__":
    run_pipeline()
