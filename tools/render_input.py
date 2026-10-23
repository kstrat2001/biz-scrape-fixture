#!/usr/bin/env python3
"""Renders the easy tier's model input for one case, from the committed site.

Usage: render_input.py <case> > inputs/easy/<case>.txt

The easy tier hands the model the site as text; nothing is fetched or
converted on the machine that runs the eval. This tool builds that text once,
here, and the result is committed with its hash (SHA256SUMS). It follows
web-probe's fetch step: the home page, then the first same-site link of each
kind (pricing, services, contact, about), each as a <web-page> block with its
title, meta description, JSON-LD, tel:/mailto: links and visible text. The
visible text is markdown from a real HTML parser (stdlib html.parser), the way
reader tools hand pages to models. The brief ends with the probe step's
message, framed exactly as a darkmux mission frames a prior step's output, so
`darkmux dispatch web-probe --message-from-file` sends what the mission would.
Stdlib only.
"""
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

HERE = pathlib.Path(__file__).resolve().parent.parent
ORIGIN = "https://copperleaf-cycles.example"
PROBE_MESSAGE = ("A business's website is above, as one or more `<web-page>` blocks. "
                 "Answer the questions in your instructions about this business, "
                 "using only what those pages say, as one JSON object.")
KINDS = [("pricing", re.compile(r"pric|cost|rates|fees|quote", re.I)),
         ("services", re.compile(r"servic", re.I)),
         ("contact", re.compile(r"contact", re.I)),
         ("about", re.compile(r"about", re.I))]
LIMITS = {"home": 20000}  # other pages: 8000 characters, as in web-probe
SKIP = {"script", "style", "noscript", "svg", "template", "title", "head", "iframe"}
BLOCK = {"p", "div", "section", "article", "header", "footer", "nav", "main", "aside",
         "address", "ul", "ol", "table", "form", "figure", "blockquote", "dl", "dt", "dd"}
VOID = {"br", "img", "input", "meta", "link", "hr", "source", "area", "base", "col", "embed", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.description, self.ld, self.contact = "", "", [], []
        self.links = []          # (href, label) for every <a href>
        self.out = []            # markdown pieces
        self.skip = 0
        self.in_title = self.in_ld = False
        self.ld_buf = ""
        self.a_stack = []        # [href, text pieces]
        self.cells = None

    def emit(self, s):
        if self.a_stack:
            self.a_stack[-1][1].append(s)
        elif self.cells is not None:
            self.cells[-1].append(s)
        else:
            self.out.append(s)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key in ("description", "og:description") and not self.description:
                self.description = a.get("content") or ""
        if tag == "script" and "ld+json" in (a.get("type") or ""):
            self.in_ld, self.ld_buf = True, ""
        if tag in SKIP:
            if tag not in VOID:
                self.skip += 1
            return
        if self.skip:
            return
        if tag == "br":
            self.emit("\n")
        elif re.fullmatch(r"h[1-6]", tag):
            self.emit("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.emit("\n- ")
        elif tag == "tr":
            self.cells = []
        elif tag in ("td", "th") and self.cells is not None:
            self.cells.append([])
        elif tag in BLOCK:
            self.emit("\n\n")
        elif tag == "a" and a.get("href"):
            self.a_stack.append([a["href"], []])
        elif tag == "img" and a.get("alt"):
            self.emit(f"![{a['alt']}]")
        else:
            self.emit(" ")  # adjacent inline elements stay separate words

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_ld:
            self.in_ld = False
            self.ld.append(self.ld_buf.strip())
        if tag in SKIP and tag not in VOID:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "a" and self.a_stack:
            href, parts = self.a_stack.pop()
            text = squash("".join(parts))
            self.links.append((href, text))
            if re.match(r"(tel|mailto):", href, re.I) and href.lower() not in (c.lower() for c in self.contact):
                self.contact.append(href)
            if text:
                self.emit(f"[{text}]({href})" if not href.startswith("#") else text)
        elif tag == "tr" and self.cells is not None:
            row = "| " + " | ".join(squash("".join(c)) for c in self.cells) + " |"
            self.cells = None
            self.emit("\n" + row)
        elif re.fullmatch(r"h[1-6]", tag) or tag in BLOCK or tag == "li":
            self.emit("\n")
        elif tag not in VOID:
            self.emit(" ")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_ld:
            self.ld_buf += data
        elif not self.skip:
            self.emit(data)

    def text(self):
        t = "".join(self.out).replace("\xa0", " ")
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in t.split("\n")]
        return "\n".join(ln for ln in lines if ln)


def squash(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def load(site, path):
    p = site / path.strip("/")
    p = p / "index.html" if p.is_dir() or not path.strip("/") else p
    return p.read_text(encoding="utf-8")


def block(url, kind, html):
    pg = Page()
    pg.feed(html)
    pg.close()
    ld = "".join(s + "\n" for s in pg.ld)[:6000]
    contact = "".join(c + "\n" for c in pg.contact)
    text = pg.text()[:LIMITS.get(kind, 8000)]
    return (f'<web-page url="{url}" kind="{kind}">\n<title>{squash(pg.title)}</title>\n'
            f"<meta-description>{pg.description}</meta-description>\n"
            f"<structured-data>\n{ld}</structured-data>\n<contact-links>\n{contact}</contact-links>\n"
            f"<page-text>\n{text}\n</page-text>\n</web-page>\n"), pg.links


def render(case):
    site = HERE / "site" / case
    home = ORIGIN + "/"
    out, links = block(home, "home", load(site, "/"))
    got = {}
    for href, label in links:
        if re.match(r"(mailto|tel|javascript|data):|#|//", href, re.I):
            continue
        url = urljoin(home, href.split("#")[0])
        if not url.startswith(ORIGIN + "/") or url.rstrip("/") == ORIGIN:
            continue
        for kind, rx in KINDS:
            if kind in got:
                continue
            if rx.search(url) or rx.search(label):
                got[kind] = url
                break
    for kind, _ in KINDS:
        if kind in got:
            page, _ = block(got[kind], kind, load(site, urlsplit(got[kind]).path))
            out += page
    return f"--- output of step `fetch` ---\n{out.rstrip()}\n\n{PROBE_MESSAGE}\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        sys.exit(2)
    sys.stdout.write(render(sys.argv[1]))
