#!/usr/bin/env python3
"""grade.py: required items must all be there; named optional items may
be; any other extra, or any changed spelling, fails the field. Stdlib only."""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
failed = 0

BASE = {
    "wix": {
        "business_name": "Copperleaf Cycle Works", "phone": "541-555-0142",
        "email": "hello@copperleaf-cycles.example",
        "address": "418 Tannery Row, Unit B; Marrow Falls, OR 97999",
        "hours": "Tue – Fri: 9:30 AM – 6:00 PM; Sat: 9:00 AM – 4:00 PM; Sun – Mon: Closed",
        "services": ["Basic Tune-Up", "Full Overhaul", "Flat Tire Repair", "Wheel Truing",
                     "Brake Service", "Bike Fitting", "E-Bike Service"],
        "area_served": ["Marrow Falls", "Linden Valley"],
        "prices": [{"item": i, "price": p, "page": "services"} for i, p in [
            ("Basic Tune-Up", "$79"), ("Full Overhaul", "from $189"), ("Flat Tire Repair", "$15"),
            ("Wheel Truing", "$25"), ("Brake Service", "$35"), ("Bike Fitting", "$120")]],
    },
    "wordpress": {
        "business_name": "Copperleaf Cycle Works", "phone": "(541) 555-0142",
        "email": "hello@copperleaf-cycles.example",
        "address": "418 Tannery Row, Unit B\nMarrow Falls, OR 97999",
        "hours": "Tue–Fri 9:30am–6pm\nSat 9am–4pm\nSun & Mon closed",
        "services": ["Basic tune-up", "Full overhaul", "Flat tire repair (tube included)",
                     "Wheel truing", "Brake service", "Bike fitting", "E-bike service"],
        "area_served": ["Marrow Falls", "Linden Valley"],
        "prices": [{"item": i, "price": p, "page": "pricing"} for i, p in [
            ("Basic tune-up", "$79"), ("Full overhaul", "from $189"), ("Flat tire repair", "$15"),
            ("Wheel truing", "$25 per wheel"), ("Brake service", "$35 per wheel"), ("Bike fitting", "$120")]],
    },
}


def grade(case, change):
    a = json.loads(json.dumps(BASE[case]))
    change(a)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(a, f)
    r = subprocess.run([sys.executable, str(HERE / "grade.py"), case, f.name], capture_output=True, text=True)
    return json.loads(r.stdout)


def check(name, case, change, passed, field=None):
    global failed
    rep = grade(case, change)
    ok = rep["passed"] == passed and (field is None or field in rep["failed"])
    print(("ok   " if ok else "FAIL ") + f"{case}: {name}" + ("" if ok else f" -> {rep}"))
    failed += not ok


def add(key, *items):
    return lambda a: a[key].extend(items)


def price(p):
    return {"item": "x", "price": p, "page": "services"}


for case in ("wix", "wordpress"):
    check("every required value", case, lambda a: None, True)
    check("wrong case on a service", case, lambda a: a["services"].__setitem__(1, a["services"][1].lower()), False, "services")
    check("invented extra service", case, add("services", "Bike rental"), False, "services")
    check("state added to a town", case, lambda a: a["area_served"].__setitem__(0, "Marrow Falls, OR"), False, "area_served")
    check("address lines joined by a space", case, lambda a: a.__setitem__("address", "418 Tannery Row, Unit B Marrow Falls, OR 97999"), False, "address")
    check("address lines joined by a comma", case, lambda a: a.__setitem__("address", "418 Tannery Row, Unit B, Marrow Falls, OR 97999"), False, "address")
    check("missing price", case, lambda a: a["prices"].pop(), False, "prices")
    check("optional free safety check", case, add("services", "free safety check"), True)
    check("optional twice", case, add("services", "free safety check", "free safety check"), False, "services")
    check("Call for a quote in prices", case, add("prices", price("Call for a quote")), False, "prices")
    check("Free in prices", case, add("prices", price("Free")), False, "prices")
    check("invented extra price", case, add("prices", price("$50")), False, "prices")
check("Varies in prices", "wix", add("prices", price("Varies")), False, "prices")
check("the Tune-Ups category listed as a service", "wix", add("services", "Tune-Ups"), False, "services")
check("the category in place of the service", "wix", lambda a: a["services"].__setitem__(0, "Tune-Ups"), False, "services")
check("Safety Check is not the site's spelling", "wix", add("services", "Safety Check"), False, "services")
check("the Tune-ups category listed as a service", "wordpress", add("services", "Tune-ups"), False, "services")
check("the category in place of the service", "wordpress", lambda a: a["services"].__setitem__(0, "Tune-ups"), False, "services")
check("flat tire repair under both spellings", "wordpress", add("services", "Flat tire repair"), False, "services")
check("Varies is not on the WordPress site", "wordpress", add("prices", price("Varies")), False, "prices")
sys.exit(1 if failed else 0)
