#!/usr/bin/env python3
"""Link design_ref fields in requirement JSONs based on design doc requirements lists."""
import json
from pathlib import Path

DOCS_DIR = Path(__file__).parent
REQ_DATA = DOCS_DIR / "requirements" / "data"
DES_DATA = DOCS_DIR / "design" / "data"

# Build map: requirement_id -> design_doc_id
req_to_design = {}
for f in sorted(DES_DATA.glob("*.json")):
    doc = json.loads(f.read_text())
    for req_id in doc.get("requirements", []):
        # A requirement can be covered by multiple design docs
        if req_id not in req_to_design:
            req_to_design[req_id] = []
        req_to_design[req_id].append(doc["id"])

print(f"Found {len(req_to_design)} requirement→design links")

# Update requirement JSON files
updated = 0
for f in sorted(REQ_DATA.glob("*.json")):
    doc = json.loads(f.read_text())
    changed = False
    for sec in doc.get("sections", []):
        for sub in sec.get("subsections", []):
            for req in sub.get("requirements", []):
                designs = req_to_design.get(req["id"])
                if designs:
                    new_ref = ", ".join(designs)
                    if req.get("design_ref") != new_ref:
                        req["design_ref"] = new_ref
                        changed = True
                        updated += 1
    if changed:
        f.write_text(json.dumps(doc, indent=2) + "\n")
        print(f"  Updated {f.name}")

print(f"Updated {updated} requirement design_ref fields")
