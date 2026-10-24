#!/usr/bin/env python3
"""The workloads in eval/workloads/ are generated from eval/expected.json, the
one answer key: a workload edited by hand, or an answer key edited without
regenerating them, fails here. Stdlib only."""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
failed = 0


def check(name, ok):
    global failed
    print(("ok   " if ok else "FAIL ") + name)
    failed += not ok


with tempfile.TemporaryDirectory() as tmp:
    root = pathlib.Path(tmp)
    (root / "tools").mkdir()
    (root / "eval").mkdir()
    (root / "tools" / "make_workloads.py").write_text((HERE / "tools" / "make_workloads.py").read_text())
    (root / "eval" / "expected.json").write_text((HERE / "eval" / "expected.json").read_text())
    subprocess.run([sys.executable, str(root / "tools" / "make_workloads.py")], check=True)
    fresh = sorted((root / "eval" / "workloads").glob("*.json"))
    committed = sorted((HERE / "eval" / "workloads").glob("*.json"))
    check("the same workloads are committed as generated", [p.name for p in fresh] == [p.name for p in committed])
    for p in fresh:
        check(f"{p.name}: matches eval/expected.json", (HERE / "eval" / "workloads" / p.name).read_text() == p.read_text())

fixture = json.loads((HERE / ".fixture.json").read_text())
for p in committed:
    w = json.loads(p.read_text())["workload"]
    check(f"{p.name}: binds this fixture", w["requires_fixture"] == fixture["satisfies"])
    check(f"{p.name}: lives in the fixture's eval_dir", p.relative_to(HERE).parts[0] == fixture["eval_dir"])
sys.exit(1 if failed else 0)
