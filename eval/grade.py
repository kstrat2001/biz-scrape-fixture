#!/usr/bin/env python3
"""Grades one answer. Usage: grade.py <case> <answer-file>

A scalar field passes when the answer's value, trimmed, equals one accepted
spelling. A list field passes when each required item is matched by its own answer
item and every other answer item matches one of the field's named optional
items (each used once). `prices` compares each item's
`price`. Nothing else is normalized: case, punctuation and inner spacing count.
Prints a JSON report; exits 0 on pass, 1 on fail.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent


def parse(text):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    obj, _ = json.JSONDecoder().raw_decode(t[t.find("{"):])
    return obj


def list_ok(got, groups, optional):
    if not all(isinstance(g, str) for g in got):
        return False
    left = [g.strip() for g in got]
    for accepted in groups:
        hit = next((g for g in left if g in accepted), None)
        if hit is None:
            return False
        left.remove(hit)
    spare = list(optional)
    for g in left:
        o = next((o for o in spare if g in o), None)
        if o is None:
            return False
        spare.remove(o)
    return True


def main():
    case, path = sys.argv[1], pathlib.Path(sys.argv[2])
    exp = json.loads((HERE / "expected.json").read_text())[case]
    try:
        a = parse(path.read_text())
    except (ValueError, OSError) as e:
        print(json.dumps({"case": case, "passed": False, "error": str(e)}))
        return 1
    f = {}
    optional = exp.pop("optional")
    for k, accepted in exp.items():
        v = a.get(k)
        if k == "prices":
            items = [p.get("price") for p in v] if isinstance(v, list) and all(isinstance(p, dict) for p in v) else None
            f[k] = items is not None and list_ok(items, accepted, optional.get(k, []))
        elif isinstance(accepted[0], list):
            f[k] = isinstance(v, list) and list_ok(v, accepted, optional.get(k, []))
        else:
            f[k] = isinstance(v, str) and v.strip() in accepted
    rep = {"case": case, "passed": all(f.values()), "fields": f,
           "failed": [k for k, ok in f.items() if not ok]}
    print(json.dumps(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
