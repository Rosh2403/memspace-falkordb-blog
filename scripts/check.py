#!/usr/bin/env python3
"""Pre-deploy checks for the static site. Exits non-zero on any problem.

    python3 scripts/check.py

Checks every page for: internal links and #anchors that point nowhere, missing
local assets, duplicate ids, images without alt text, raw '<' left in code, and
an ontology catalog that has drifted from data/ontology-*.json.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = {"/": "index.html", "/ontology": "ontology.html", "/falkordb": "falkordb.html", "/404": "404.html"}


def main() -> int:
    problems: list[str] = []
    html = {route: (ROOT / f).read_text() for route, f in PAGES.items()}
    ids = {route: re.findall(r'\sid="([^"]+)"', s) for route, s in html.items()}

    for route, s in html.items():
        name = PAGES[route]
        seen = ids[route]
        for dup in sorted({i for i in seen if seen.count(i) > 1}):
            problems.append(f"{name}: duplicate id #{dup}")
        for url in re.findall(r'\s(?:href|src)="([^"]+)"', s):
            if url.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            path, _, frag = url.partition("#")
            target = route if path == "" else path
            if target in PAGES:
                if frag and frag not in ids[target]:
                    problems.append(f"{name}: link to missing anchor {url}")
            elif not (ROOT / path.lstrip("/")).exists():
                problems.append(f"{name}: missing file {url}")
        for img in re.findall(r"<img\b[^>]*>", s):
            if " alt=" not in img:
                problems.append(f"{name}: image without alt text: {img[:70]}")
        for code in re.findall(r"<code\b[^>]*>(.*?)</code>", s, re.S):
            if re.search(r"<(?=[-= ])", code):
                problems.append(f"{name}: unescaped '<' in a code sample")

    exports = sorted((ROOT / "data").glob("ontology-*.json"))
    if exports:
        data = json.loads(exports[-1].read_text())
        page = html["/ontology"]
        rows = len(re.findall(r"<tr><td><code>[A-Z_]+</code></td><td><span class=\"ends\">", page))
        cards = page.count('class="type-card"')
        if rows != len(data["relationships"]) or cards != len(data["types"]):
            problems.append(
                f"ontology.html: catalog shows {cards} types and {rows} relationships, "
                f"{exports[-1].name} has {len(data['types'])} and {len(data['relationships'])}. "
                "Run scripts/build-catalog.py."
            )

    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(PAGES)} pages, links, anchors, assets, alt text and catalog all check out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
