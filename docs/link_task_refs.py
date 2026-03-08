#!/usr/bin/env python3
"""Populate requirement JSONs with task and test references from task data files.

Reads all docs/tasks/data/*.json, builds a map of requirement_id -> [task_ids]
and requirement_id -> [test_ids], then updates docs/requirements/data/*.json
with the `tasks` and `tests` arrays.
"""
import json
from pathlib import Path

TASK_DIR = Path(__file__).parent / "tasks" / "data"
REQ_DIR = Path(__file__).parent / "requirements" / "data"


def main():
    # Build maps: req_id -> [task_ids], req_id -> [test entries]
    req_to_tasks: dict[str, list[str]] = {}
    req_to_tests: dict[str, list[dict]] = {}

    for task_file in sorted(TASK_DIR.glob("*.json")):
        tasks = json.loads(task_file.read_text())
        for task in tasks:
            task_id = task["id"]
            for req_id in task.get("requirements", []):
                req_to_tasks.setdefault(req_id, []).append(task_id)
                for test in task.get("tests", []):
                    req_to_tests.setdefault(req_id, []).append({
                        "id": test["id"],
                        "task_id": task_id,
                        "description": test["description"],
                        "type": test["type"],
                        "file": test["file"],
                    })

    # Update requirement JSONs
    updated_reqs = 0
    for req_file in sorted(REQ_DIR.glob("*.json")):
        doc = json.loads(req_file.read_text())
        changed = False
        for section in doc.get("sections", []):
            for subsection in section.get("subsections", []):
                for req in subsection.get("requirements", []):
                    rid = req["id"]
                    new_tasks = sorted(set(req_to_tasks.get(rid, [])))
                    new_tests = req_to_tests.get(rid, [])
                    # Deduplicate tests by id
                    seen = set()
                    deduped_tests = []
                    for t in new_tests:
                        if t["id"] not in seen:
                            seen.add(t["id"])
                            deduped_tests.append(t)
                    if new_tasks != req.get("tasks", []) or deduped_tests != req.get("tests", []):
                        req["tasks"] = new_tasks
                        req["tests"] = deduped_tests
                        changed = True
                        updated_reqs += 1

        if changed:
            req_file.write_text(json.dumps(doc, indent=2) + "\n")
            print(f"  Updated {req_file.name}")

    linked = len([r for r, ts in req_to_tasks.items() if ts])
    total_tests = sum(len(ts) for ts in req_to_tests.values())
    print(f"\nLinked {linked} requirements to tasks, {total_tests} test references")
    print(f"Updated {updated_reqs} requirement entries")


if __name__ == "__main__":
    main()
