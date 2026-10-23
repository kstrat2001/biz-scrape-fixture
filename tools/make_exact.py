#!/usr/bin/env python3
"""Writes expected.json: every accepted answer, spelled exactly as the
case's pages show it. A value the pages split over lines (address, hours) is
accepted with its lines joined by "; ", as the role asks, or by line breaks. A list answer must hold every
required item and may also hold the named optional ones: things the site does
say that a careful reader could fairly list (a free safety check as a
service). Something the role explicitly excludes is not one of them: free or
on-request items belong in pricing_note, not prices. A service listed twice, once under each of the
site's spellings, is not one of them: the role asks for one entry per service. Any other extra fails the field.
An answer passes only when every graded field matches an accepted spelling
after trimming outer whitespace. Stdlib only.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
JOINS = ["; ", "\n"]


def joined(*sources):
    return sorted({j.join(lines) for lines in sources for j in JOINS})


HOLIDAY = "Holiday hours: closed Thanksgiving Day and December 25."


def with_holiday(spellings):
    """The pages' holiday note is real hours text, so it may follow the hours."""
    return sorted(set(spellings) | {h + j + HOLIDAY for h in spellings for j in JOINS})


ADDRESS = ("418 Tannery Row, Unit B", "Marrow Falls, OR 97999")

CASES = {
    "wordpress": {
        "phone": ["(541) 555-0142", "tel:+15415550142", "+15415550142"],
        "hours": joined(("Tue–Fri 9:30am–6pm", "Sat 9am–4pm", "Sun & Mon closed")),
        "services": [
            ["Basic tune-up"],
            ["Full overhaul"],
            ["Flat tire repair (tube included)", "Flat tire repair"],
            ["Wheel truing"],
            ["Brake service"],
            ["Bike fitting"],
            ["E-bike service"],
        ],
        "prices": [["$79"], ["from $189"], ["$15"], ["$25 per wheel"], ["$35 per wheel"], ["$120"]],
        "optional": {
            "services": [["free safety check"], ["same-day service"]],
        },
    },
    "wix": {
        "phone": ["541-555-0142", "tel:5415550142", "5415550142"],
        "hours": joined(
            ("Tue – Fri: 9:30 AM – 6:00 PM", "Sat: 9:00 AM – 4:00 PM", "Sun – Mon: Closed"),
            ("Monday: Closed", "Tuesday – Friday: 9:30 AM – 6:00 PM", "Saturday: 9:00 AM – 4:00 PM", "Sunday: Closed"),
        ),
        "services": [
            ["Basic Tune-Up"],
            ["Full Overhaul"],
            ["Flat Tire Repair"],
            ["Wheel Truing"],
            ["Brake Service"],
            ["Bike Fitting"],
            ["E-Bike Service"],
        ],
        "prices": [["$79", "$79 79 US dollars"], ["from $189", "from $189 from 189 US dollars"],
                   ["$15", "$15 15 US dollars"], ["$25", "$25 25 US dollars"],
                   ["$35", "$35 35 US dollars"], ["$120", "$120 120 US dollars"]],
        "optional": {
            "services": [["free safety check"], ["same-day service"]],
        },
    },
}

out = {}
for case, c in CASES.items():
    out[case] = {
        "business_name": ["Copperleaf Cycle Works"],
        "phone": c["phone"],
        "email": ["hello@copperleaf-cycles.example"],
        "address": joined(ADDRESS),
        "hours": with_holiday(c["hours"]),
        "services": c["services"],
        "area_served": [["Marrow Falls"], ["Linden Valley", "the Linden Valley"]],
        "prices": c["prices"],
        "optional": c["optional"],
    }
(HERE / "expected.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
