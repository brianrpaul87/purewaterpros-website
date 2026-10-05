#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = "https://www.purewaterpros.ca"
SITEMAP = ROOT / "sitemap.xml"

STALE_PATTERNS = [
    re.compile(r"Now booking September", re.I),
    re.compile(r"soft launch", re.I),
    re.compile(r"Pre-launch:", re.I),
    re.compile(r"Opening August 2026", re.I),
    re.compile(r"Request August follow-up", re.I),
    re.compile(r"preparing to provide scheduled", re.I),
    re.compile(r"should not wait for launch", re.I),
    re.compile(r"905-242-3846"),
    re.compile(r"705-768-7273"),
    re.compile(r"Durham, Peterborough", re.I),
    re.compile(r"Omemee", re.I),
]

SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.in_title = False
        self.description = []
        self.robots = []
        self.canonicals = []
        self.refs = []
        self.jsonld = []
        self._jsonld_active = False
        self._jsonld_buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            name = (a.get("name") or "").lower()
            if name == "description":
                self.description.append(a.get("content", "").strip())
            elif name == "robots":
                self.robots.append(a.get("content", "").strip())
        if tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonicals.append(a.get("href", "").strip())
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._jsonld_active = True
            self._jsonld_buf = []
        for attr in ("href", "src", "action"):
            v = a.get(attr)
            if v:
                self.refs.append(v)
        srcset = a.get("srcset")
        if srcset:
            for candidate in srcset.split(","):
                v = candidate.strip().split()[0] if candidate.strip() else ""
                if v:
                    self.refs.append(v)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self._jsonld_active:
            self._jsonld_active = False
            self.jsonld.append("".join(self._jsonld_buf).strip())
            self._jsonld_buf = []

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self._jsonld_active:
            self._jsonld_buf.append(data)


def fail(errors, message):
    errors.append(message)


def url_to_repo_path(url: str) -> Path | None:
    if not url or url.startswith("#") or url.startswith(SKIP_SCHEMES):
        return None
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme and parsed.netloc:
        if f"{parsed.scheme}://{parsed.netloc}".lower() != DOMAIN.lower():
            return None
        path = parsed.path
    else:
        path = parsed.path
    path = urllib.parse.unquote(path)
    if not path or path == "/":
        return ROOT / "index.html"
    if path.endswith("/"):
        return ROOT / path.lstrip("/") / "index.html"
    return ROOT / path.lstrip("/")


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def normalize_internal_url(ref: str, base_url: str) -> str | None:
    if not ref or ref.startswith(SKIP_SCHEMES):
        return None
    absolute = urllib.parse.urljoin(base_url, ref)
    parsed = urllib.parse.urlsplit(absolute)
    if f"{parsed.scheme}://{parsed.netloc}".lower() != DOMAIN.lower():
        return None
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, ""))


def list_internal_urls() -> int:
    urls: set[str] = set()
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {".git", ".github", "docs", "_deploy"}:
            continue
        parser = parse_page(path)
        if parser.canonicals:
            base_url = parser.canonicals[0]
        elif rel.as_posix() == "index.html":
            base_url = DOMAIN + "/"
        elif rel.name == "index.html":
            base_url = DOMAIN + "/" + rel.parent.as_posix().strip("/") + "/"
        else:
            base_url = DOMAIN + "/" + rel.as_posix()
        for ref in parser.refs:
            normalized = normalize_internal_url(ref, base_url)
            if normalized:
                urls.add(normalized)
    for url in sorted(urls):
        print(url)
    return 0


def main() -> int:
    if "--list-internal-urls" in sys.argv:
        return list_internal_urls()
    errors: list[str] = []

    try:
        tree = ET.parse(SITEMAP)
    except Exception as e:
        print(f"ERROR: sitemap.xml is not valid XML: {e}")
        return 1

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    entries = tree.findall("sm:url", ns)
    locs = []
    for entry in entries:
        loc = (entry.findtext("sm:loc", default="", namespaces=ns) or "").strip()
        lastmod = (entry.findtext("sm:lastmod", default="", namespaces=ns) or "").strip()
        if not loc:
            fail(errors, "Sitemap entry missing <loc>")
            continue
        if loc in locs:
            fail(errors, f"Duplicate sitemap URL: {loc}")
        locs.append(loc)
        if not loc.startswith(DOMAIN + "/"):
            fail(errors, f"Sitemap URL is not canonical www HTTPS URL: {loc}")
        if lastmod:
            try:
                d = date.fromisoformat(lastmod)
                if d > date.today():
                    fail(errors, f"Sitemap lastmod is in the future: {loc} -> {lastmod}")
            except ValueError:
                fail(errors, f"Invalid sitemap lastmod date: {loc} -> {lastmod}")

    for loc in locs:
        path = url_to_repo_path(loc)
        if path is None or not path.is_file():
            fail(errors, f"Sitemap URL has no matching repository file: {loc}")
            continue
        parser = parse_page(path)
        title = "".join(parser.title).strip()
        if not title:
            fail(errors, f"Missing <title>: {path.relative_to(ROOT)}")
        if len(parser.description) != 1 or not parser.description[0]:
            fail(errors, f"Expected one non-empty meta description: {path.relative_to(ROOT)}")
        if len(parser.canonicals) != 1:
            fail(errors, f"Expected exactly one canonical URL: {path.relative_to(ROOT)}")
        elif parser.canonicals[0] != loc:
            fail(errors, f"Canonical mismatch: {path.relative_to(ROOT)} -> {parser.canonicals[0]} != {loc}")
        if any("noindex" in r.lower() for r in parser.robots):
            fail(errors, f"Sitemap page is noindex: {path.relative_to(ROOT)}")
        for idx, raw in enumerate(parser.jsonld, 1):
            if not raw:
                fail(errors, f"Empty JSON-LD block #{idx}: {path.relative_to(ROOT)}")
                continue
            try:
                json.loads(raw)
            except Exception as e:
                fail(errors, f"Invalid JSON-LD block #{idx} in {path.relative_to(ROOT)}: {e}")

    # Thank-you is intentionally noindex but must remain complete and functional.
    thank_you = ROOT / "thank-you.html"
    if not thank_you.is_file():
        fail(errors, "Missing thank-you.html")
    else:
        p = parse_page(thank_you)
        if not any("noindex" in r.lower() for r in p.robots):
            fail(errors, "thank-you.html must remain noindex")
        if p.canonicals != [DOMAIN + "/thank-you.html"]:
            fail(errors, "thank-you.html canonical is missing or incorrect")

    # Form endpoint and homepage wiring.
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for needle in [
        'action="/contact.php"',
        'method="post"',
        'name="name" required',
        'name="email" required',
        'name="consent" required',
    ]:
        if needle not in home:
            fail(errors, f"Homepage service form is missing expected wiring: {needle}")
    if not (ROOT / "contact.php").is_file():
        fail(errors, "Missing contact.php form handler")

    # Crawl all deployable text sources for known stale migration copy.
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {".git", ".github", "docs", "_deploy"}:
            continue
        if path.suffix.lower() not in {".html", ".js", ".php", ".xml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in STALE_PATTERNS:
            if pattern.search(text):
                fail(errors, f"Stale Ontario/pre-launch text '{pattern.pattern}' found in {rel}")

    if errors:
        print("PUBLIC SITE VERIFICATION FAILED")
        for e in errors:
            print(f" - {e}")
        return 1

    print(f"PUBLIC SITE VERIFICATION PASSED: {len(locs)} sitemap URLs validated.")
    print(" - Canonicals, titles, descriptions and JSON-LD validated")
    print(" - Internal links/assets will be checked against live production after deployment")
    print(" - Service request form wiring checked")
    print(" - Stale Ontario/pre-launch text scan passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
