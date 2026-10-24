#!/usr/bin/env python3
"""Writes eval/workloads/biz-scrape-easy-<case>.json, one darkmux lab workload per
case, from eval/expected.json: the reply must match every graded field
exactly (after trimming the ends), with each field's accepted spellings as
anyOf. Stdlib only.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent


def one(spellings):
    return spellings[0] if len(spellings) == 1 else {"anyOf": spellings}


exact = json.loads((HERE / "eval" / "expected.json").read_text())
(HERE / "eval" / "workloads").mkdir(parents=True, exist_ok=True)
for case, fields in exact.items():
    optional = fields.pop("optional")
    expect = {}
    for k, v in fields.items():
        if isinstance(v[0], list):
            entry = (lambda g: {"price": one(g)}) if k == "prices" else one
            expect[k] = {"items": [entry(g) for g in v],
                         "optional": [entry(g) for g in optional.get(k, [])]}
        else:
            expect[k] = one(v)
    wid = f"biz-scrape-easy-{case}"
    w = {"schema_version": "1.1", "workload": {
        "id": wid, "provider": "prompt", "role": "web-probe",
        "requires_fixture": "biz-scrape-fixture@1.1",
        "promptFile": f"inputs/easy/{case}.txt", "replyRoom": "context",
        "verify": {"expect": expect}}}
    (HERE / "eval" / "workloads" / f"{wid}.json").write_text(json.dumps(w, indent=2, ensure_ascii=False) + "\n")
