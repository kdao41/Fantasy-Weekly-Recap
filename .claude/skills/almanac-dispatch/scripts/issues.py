"""List the PDF dispatches in almanac/ so the site can link each league's newest issue.
usage: python3 -I issues.py <repo_dir>   -> writes <repo_dir>/almanac/issues.json, e.g. {"aggtown": {"2026": [5, 6]}}"""
import json, pathlib, re, sys

root = pathlib.Path(sys.argv[1]) / "almanac"
issues = {}
for pdf in sorted(root.glob("*/*/week-*.pdf")):
    m = re.fullmatch(r"week-(\d+)\.pdf", pdf.name)
    if m:
        issues.setdefault(pdf.parent.parent.name, {}).setdefault(pdf.parent.name, []).append(int(m.group(1)))
(root / "issues.json").write_text(json.dumps(issues, indent=1, sort_keys=True) + "\n")
print(json.dumps(issues))
