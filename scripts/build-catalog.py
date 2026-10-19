#!/usr/bin/env python3
"""Fill the ontology page's catalog from the exported schema.

The schema lives in pranavjana/shared-memory-mcp (src/ontology.ts). Export it to
data/ontology-<version>.json, then run:

    python3 scripts/build-catalog.py data/ontology-1.2.0.json

It rewrites the blocks between <!-- catalog:NAME:start --> and
<!-- catalog:NAME:end --> in ontology.html. Everything else is left untouched.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "ontology.html"

# Our grouping for readers. The schema itself is flat.
FAMILIES = [
    ("People and relationships", "Who knows whom. Direction matters, and none of these grant access to anything.",
     ["KNOWS", "FRIEND_OF", "FAMILY_OF", "PARENT_OF", "SIBLING_OF", "PARTNER_OF", "COLLEAGUE_OF", "REPORTS_TO"]),
    ("Work and learning", "Where someone works or studies, what they work on, and what they can do.",
     ["WORKS_AT", "STUDIES_AT", "MEMBER_OF_ORGANIZATION", "WORKS_ON", "HAS_SKILL", "HAS_ROLE"]),
    ("Places and events", "Where things are, and what happened when.",
     ["LIVES_IN", "LOCATED_AT", "HAS_PARTICIPANT", "ORGANIZED_BY", "STARTS_AT", "ENDS_AT", "OCCURRED_AT"]),
    ("Wants and worries", "Desired outcomes and concerns, which are never decisions or diagnoses.",
     ["WANTS", "CONCERNED_ABOUT", "CONTRIBUTES_TO"]),
    ("Tasks", "Assignment, acceptance and completion are separate facts.",
     ["PART_OF", "ASSIGNED_TO", "ACCEPTED_BY", "COMPLETED_BY", "DEPENDS_ON", "HAS_STATUS", "DUE_AT"]),
    ("Preferences and habits", "Preferences keep their context. Habits are recurring, not reminders.",
     ["PREFERENCE_OF", "APPLIES_TO", "HAS_VALUE", "LIKES", "DISLIKES", "PRACTICES", "HAS_FREQUENCY"]),
    ("Decisions", "Who chose, and the reason they actually gave.",
     ["DECIDED_BY", "HAS_REASON"]),
    ("Things", "What someone owns or uses.",
     ["OWNS", "USES"]),
    ("Money", "One debt per obligation. No balances are ever calculated.",
     ["OWES", "OWED_TO", "FOR_CONTEXT", "HAS_AMOUNT", "HAS_CURRENCY", "HAS_PAYMENT_STATUS"]),
    ("Fallback", "Used only when nothing more precise fits.",
     ["ABOUT"]),
]

e = html.escape


def human(rel_id: str) -> str:
    return rel_id.lower().replace("_", " ")


def endpoint(rel: dict) -> str:
    src = " / ".join(rel["from"])
    if rel.get("value"):
        v = rel["value"]
        fmt = v["type"]
        if v.get("values"):
            fmt += ": " + ", ".join(v["values"])
        return f'<span class="ends"><b>{e(src)}</b> = {e(fmt)}</span>'
    to = rel["to"]
    dst = "any type" if len(to) >= 13 else " / ".join(to)
    src = "any type" if len(rel["from"]) >= 13 else src
    return f'<span class="ends"><b>{e(src)}</b> → <b>{e(dst)}</b></span>'


def build(data: dict) -> dict:
    rels = {r["id"]: r for r in data["relationships"]}
    grouped = [rid for _, _, ids in FAMILIES for rid in ids]
    missing = sorted(set(rels) - set(grouped))
    unknown = sorted(set(grouped) - set(rels))
    if missing or unknown:
        sys.exit(f"Family list is out of date. Missing: {missing}. Unknown: {unknown}.")

    rules = "\n".join(f"          <li>{e(rule)}</li>" for rule in data["rules"])
    rules_html = f'        <ol class="rules">\n{rules}\n        </ol>'

    cards = []
    for t in data["types"]:
        outgoing = [r["id"] for r in data["relationships"] if t["id"] in r["from"] and r["id"] != "ABOUT"]
        chips = "".join(f'<span class="chip">{e(human(r))}</span>' for r in outgoing) or '<span class="chip">about</span>'
        cards.append(
            f'          <div class="type-card" data-type="{e(t["id"])}">\n'
            f'            <h3>{e(t["name"])}</h3>\n'
            f'            <p>{e(t["description"].rstrip(".") + ".")}</p>\n'
            f'            <div class="rels">{chips}</div>\n'
            f'          </div>'
        )
    types_html = '        <div class="type-grid">\n' + "\n".join(cards) + "\n        </div>"

    tables = []
    for name, blurb, ids in FAMILIES:
        rows = "\n".join(
            f'              <tr><td><code>{e(rid)}</code></td><td>{endpoint(rels[rid])}</td><td>{e(rels[rid]["description"])}</td></tr>'
            for rid in ids
        )
        tables.append(
            '        <div class="table-scroll">\n'
            '          <table class="catalog">\n'
            f'            <caption>{e(name)} <span class="ends">· {len(ids)}</span><br><span class="ends" style="font-family:var(--sans)">{e(blurb)}</span></caption>\n'
            '            <thead><tr><th scope="col">Relationship</th><th scope="col">From → to</th><th scope="col">Meaning</th></tr></thead>\n'
            f'            <tbody>\n{rows}\n            </tbody>\n'
            '          </table>\n'
            '        </div>'
        )
    return {"rules": rules_html, "types": types_html, "relationships": "\n".join(tables)}


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    data = json.loads(Path(sys.argv[1]).read_text())
    blocks = build(data)
    page = PAGE.read_text()
    for name, body in blocks.items():
        pattern = re.compile(rf"(<!-- catalog:{name}:start -->)(.*?)(\s*<!-- catalog:{name}:end -->)", re.S)
        if not pattern.search(page):
            sys.exit(f"Marker catalog:{name} not found in {PAGE.name}")
        page = pattern.sub(lambda m: m.group(1) + "\n" + body + m.group(3), page)
    PAGE.write_text(page)
    print(f"ontology.html: {len(data['types'])} types, {len(data['relationships'])} relationships, {len(data['rules'])} rules (schema {data['version']})")


if __name__ == "__main__":
    main()
