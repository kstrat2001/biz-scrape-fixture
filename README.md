# biz-scrape-fixture

darkmux evals that are not coding tests. A model reads a fake small-business
website and answers as JSON. The answer is graded deterministically against
the site's own text: every graded value must match exactly, pass or fail.

The business, Copperleaf Cycle Works in Marrow Falls, is invented. Phone
numbers use the 555-01xx range reserved for fiction; the domain is `.example`,
which can never resolve.

## Evals

Each file in `evals/` is one eval: one row on evals.darkmux.com, with its own
role and pass rule. A run is one eval on one model on one machine, and passes
when every case passes.

| Eval | How the model gets the site | Role |
|---|---|---|
| `easy` | handed over as committed text (home page plus linked services, contact and about pages) | `web-probe` (no tools) |

Medium (the model fetches the URL itself) and hard (it also follows links to
find facts on other pages) come later, with a tool-using role.

## Cases

The same shop, with the same facts, built with two site builders:

- `wordpress`: Astra theme, Yoast SEO, Contact Form 7, cookie banner.
- `wix`: Thunderbolt server render, generated ids, Bookings service cards.

Both carry a parts-orders-only phone number and a holiday-hours note, as real
sites do. Two departures from real sites: links are root-relative (so they work
from a local server), and Wix's very large inline JSON and script blocks are cut
to a few KB so a page fits a small model's context. `tools/` holds the
generators for the inner pages; `tools/build.sh` regenerates them and checks
them against `SHA256SUMS`.

## Model input (easy)

Nothing is fetched or converted on the machine that runs the easy eval. The
text the model reads is in `inputs/easy/<case>.txt`, made once from the
committed site by `tools/render_input.py` (a stdlib HTML parser producing
markdown, in web-probe's `<web-page>` block format) and listed in
`SHA256SUMS`. `python3 test/test_inputs.py` checks that the committed inputs
match a fresh render and carry every graded answer word for word.

The role is the fixture's own `web-probe` in `roles/`, pinned by
`role_sha256` in `evals/easy.json`. It is darkmux's web-probe with the
directions made explicit for an eval: every graded value is copied exactly
from the site, a value written over several lines has its lines joined by
"; ", services are listed once each under their specific name (a heading that
groups services is not one), prices are one entry per price row, and free or
on-request items go in `pricing_note`.

## Running it

`eval/workloads/biz-scrape-easy-<case>.json` are darkmux lab workloads (provider
`prompt`, needs darkmux 5.5 or later): `darkmux lab run biz-scrape-easy-wix`
with this fixture registered. A model may reply until its context window is
full: the reply room is the profile's context window less the prompt, and both
are recorded with the run, since context is the machine's configuration, not
the eval's.

`run-one.sh` runs one case outside the lab, with `darkmux dispatch
--message-from-file`, the role installed into a separate `DARKMUX_HOME`, and
the same grading.

## Grading

`eval/expected.json` (written by `tools/make_exact.py`) holds every accepted answer
for the eight graded fields: business name, phone, email, address, hours,
services, area served and prices. A value passes when, trimmed, it equals one
accepted spelling exactly: case, punctuation and spacing all count. The
accepted spellings are the site's own: the phone as shown or as its `tel:`
link, the address and hours with their lines joined by "; " or by line breaks,
and the hours with or without the holiday note. A list field must hold every
required item, each once, and may also hold the named optional items, things
the site does say that the role leaves room to list (a free safety check as a
service). Any other extra fails the field. The other web-probe fields are not
graded.

The lab workloads in `eval/workloads/` carry the same rule as `verify.expect`
(written by `tools/make_workloads.py` from `eval/expected.json`, the one answer
key; `python3 test/test_workloads.py` fails if they drift); `eval/grade.py
<case> <answer.json>` is the stdlib reference, and `python3 test/test_grade.py`
its self-test.

## The eval is defined here

From 1.1 this repository defines the whole eval. `eval/` holds the darkmux
workloads, the answer key and the reference grader; darkmux processes the eval
and does not define it. `eval/` is never copied into the model's sandbox, and
runs report the sha256 of the workload document they used.
