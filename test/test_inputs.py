#!/usr/bin/env python3
"""The committed easy-tier inputs are what tools/render_input.py makes from the
committed site, and they carry every graded answer word for word. Stdlib only."""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
failed = 0


def check(name, ok):
    global failed
    print(("ok   " if ok else "FAIL ") + name)
    failed += not ok


expected = json.loads((HERE / "eval" / "expected.json").read_text())
for case in ("wordpress", "wix"):
    committed = (HERE / "inputs" / "easy" / f"{case}.txt").read_text()
    rendered = subprocess.run([sys.executable, str(HERE / "tools" / "render_input.py"), case],
                              capture_output=True, text=True, check=True).stdout
    check(f"{case}: committed input matches a fresh render", committed == rendered)
    check(f"{case}: four pages", committed.count("<web-page ") == 4)
    exp = dict(expected[case])
    optional = exp.pop("optional")
    for field, accepted in exp.items():
        groups = accepted if isinstance(accepted[0], list) else [accepted]
        for g in groups + optional.get(field, []):
            check(f"{case}: {field} {g[0]!r} is in the input as written", any(s in committed for s in g))
    check(f"{case}: no price run together with its screen-reader text", "$7979" not in committed)
    check(f"{case}: no leftover character references", "&amp;" not in committed and "&ndash;" not in committed)
    check(f"{case}: ends with the probe message", committed.rstrip().endswith("as one JSON object."))

sys.exit(1 if failed else 0)
