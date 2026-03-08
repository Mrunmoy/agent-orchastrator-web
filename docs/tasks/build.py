#!/usr/bin/env python3
"""Bundle task JSON files into _bundle.js for offline HTML viewing."""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUT = Path(__file__).parent / "_bundle.js"


def main():
    tasks = {}
    for p in sorted(DATA_DIR.glob("*.json")):
        doc = json.loads(p.read_text())
        key = p.stem  # e.g. "foundation-tasks"
        tasks[key] = doc
    js = f"window.__TASK_DATA__ = {json.dumps(tasks, indent=2)};\n"
    OUT.write_text(js)
    total = sum(len(v) for v in tasks.values())
    total_tests = sum(len(t.get("tests", [])) for v in tasks.values() for t in v)
    print(f"Bundled {len(tasks)} task files, {total} tasks, {total_tests} test cases -> {OUT}")


if __name__ == "__main__":
    main()
