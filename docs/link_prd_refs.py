#!/usr/bin/env python3
"""Link PRD (product) requirements to tasks via their child requirements.

PRD requirements are high-level. They map to specific OR/IN/MG/UI/BE requirements
which already have tasks. This script propagates task/test links upward.

Also links BE-R requirements that describe specific API endpoints to relevant tasks
by matching task descriptions and requirement text.
"""
import json
from pathlib import Path

TASK_DIR = Path(__file__).parent / "tasks" / "data"
REQ_DIR = Path(__file__).parent / "requirements" / "data"
DESIGN_DIR = Path(__file__).parent / "design" / "data"

# Manual mapping: PRD requirement -> child requirement IDs that implement it
PRD_TO_CHILDREN = {
    "PRD-001": ["OR-R001", "OR-R002", "OR-R003"],
    "PRD-002": ["OR-R003", "OR-R011"],
    "PRD-003": ["OR-R010"],
    "PRD-004": ["OR-R020"],
    "PRD-005": ["OR-R021"],
    "PRD-006": ["OR-R050", "OR-R051"],
    "PRD-007": ["OR-R070"],
    "PRD-008": ["OR-R070", "OR-R071"],
    "PRD-009": ["IN-R090", "IN-R091", "IN-R092"],
    "PRD-010": ["OR-R061"],
    "PRD-011": ["MG-R031"],
    "PRD-012": ["MG-R030", "OR-R080"],
    "PRD-013": ["MG-R001", "MG-R002"],
    "PRD-014": ["MG-R011", "MG-R020"],
    "PRD-015": ["OR-R080", "OR-R081"],
    "PRD-016": ["UI-R040", "UI-R041"],
    "PRD-017": ["UI-R010", "UI-R012"],
    "PRD-018": ["UI-R050", "UI-R051"],
    "PRD-019": ["UI-R001", "UI-R002"],
    "PRD-020": ["BE-R060"],
    "PRD-021": ["IN-R031", "MG-R020"],
    "PRD-022": ["IN-R031", "OR-R052"],
}

# Manual mapping: BE-R API requirements -> design refs and task IDs
BE_API_LINKS = {
    "BE-R070": {"design_ref": "DES-01, DES-02", "tasks": ["T-201"]},
    "BE-R080": {"design_ref": "DES-01, DES-02", "tasks": ["T-212", "T-213"]},
    "BE-R081": {"design_ref": "DES-01, DES-02", "tasks": ["T-213"]},
    "BE-R110": {"design_ref": "DES-01, DES-06", "tasks": ["T-505"]},
    "BE-R130": {"design_ref": "DES-07", "tasks": ["T-601", "T-602", "T-603", "T-604"]},
    "BE-R132": {"design_ref": "DES-07", "tasks": ["T-606"]},
    # IN integration gaps
    "IN-R070": {"tasks": ["T-703", "T-705"]},
    "IN-R100": {"tasks": ["T-702"]},
    "IN-R101": {"tasks": ["T-706"]},
}


def main():
    # Load all tasks and build req->task/test maps
    req_to_tasks: dict[str, list[str]] = {}
    req_to_tests: dict[str, list[dict]] = {}

    for tf in sorted(TASK_DIR.glob("*.json")):
        for task in json.loads(tf.read_text()):
            for rid in task.get("requirements", []):
                req_to_tasks.setdefault(rid, []).append(task["id"])
                for test in task.get("tests", []):
                    req_to_tests.setdefault(rid, []).append({
                        "id": test["id"],
                        "task_id": task["id"],
                        "description": test["description"],
                        "type": test["type"],
                        "file": test["file"],
                    })

    # Build PRD -> tasks/tests by traversing children
    prd_tasks: dict[str, set] = {}
    prd_tests: dict[str, list] = {}
    for prd_id, children in PRD_TO_CHILDREN.items():
        tasks = set()
        tests = []
        for child_id in children:
            tasks.update(req_to_tasks.get(child_id, []))
            tests.extend(req_to_tests.get(child_id, []))
        prd_tasks[prd_id] = tasks
        prd_tests[prd_id] = tests

    # Update requirement JSONs
    updated = 0
    for rf in sorted(REQ_DIR.glob("*.json")):
        doc = json.loads(rf.read_text())
        changed = False
        for sec in doc.get("sections", []):
            for sub in sec.get("subsections", []):
                for req in sub.get("requirements", []):
                    rid = req["id"]

                    # PRD propagation
                    if rid in prd_tasks:
                        new_tasks = sorted(prd_tasks[rid])
                        # Deduplicate tests
                        seen = set()
                        new_tests = []
                        for t in prd_tests.get(rid, []):
                            if t["id"] not in seen:
                                seen.add(t["id"])
                                new_tests.append(t)
                        if new_tasks and new_tasks != req.get("tasks", []):
                            req["tasks"] = new_tasks
                            changed = True
                            updated += 1
                        if new_tests and new_tests != req.get("tests", []):
                            req["tests"] = new_tests
                            changed = True

                    # BE-R API direct links
                    if rid in BE_API_LINKS:
                        link = BE_API_LINKS[rid]
                        if "design_ref" in link and not req.get("design_ref"):
                            req["design_ref"] = link["design_ref"]
                            changed = True
                            updated += 1
                        if "tasks" in link:
                            existing = set(req.get("tasks", []))
                            new = sorted(existing | set(link["tasks"]))
                            if new != req.get("tasks", []):
                                req["tasks"] = new
                                changed = True
                                updated += 1
                            # Also add tests from those tasks
                            for tid in link["tasks"]:
                                for t in req_to_tests.get(rid, []):
                                    pass  # Already linked if req was in task.requirements
                                # Get tests from the task directly
                                for tf2 in sorted(TASK_DIR.glob("*.json")):
                                    for task in json.loads(tf2.read_text()):
                                        if task["id"] == tid:
                                            existing_tests = {t["id"] for t in req.get("tests", [])}
                                            for test in task.get("tests", []):
                                                if test["id"] not in existing_tests:
                                                    req.setdefault("tests", []).append({
                                                        "id": test["id"],
                                                        "task_id": tid,
                                                        "description": test["description"],
                                                        "type": test["type"],
                                                        "file": test["file"],
                                                    })
                                                    changed = True

        if changed:
            rf.write_text(json.dumps(doc, indent=2) + "\n")
            print(f"  Updated {rf.name}")

    print(f"\nUpdated {updated} requirement entries with propagated links")


if __name__ == "__main__":
    main()
