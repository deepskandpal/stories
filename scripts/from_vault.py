#!/usr/bin/env python3
"""Copy a piece from the Obsidian vault (/home/dk/vaults/deepanshu-kandpal/deepanshukandpal.com/)
into this site, as a thought or a writing.

The note may carry its own details in frontmatter (all optional):

    ---
    title: Learning needs to be hard
    tags: [tech]
    description: One line for search results and link previews.
    ---

Without a title, the note's first "# Heading" (or its file name) is used.

Obsidian-only pieces are converted:

  %% private note %%     -> removed (never published)
  ![[image.png|caption]] -> the image, copied into the page's folder
  [[link|text]]          -> text
  > [!note] Title        -> > **Title**

Usage:
  scripts/from_vault.py <vault-note.md> --section thoughts [--slug slug]            # update as a draft
  scripts/from_vault.py <vault-note.md> --section writings [--slug slug] --publish  # make it live, dated today

The page lands at content/<section>/<slug>/index.md, so its URL is /<section>/<slug>/.
"""

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

VAULT = Path("/home/dk/vaults")
SITE = Path(__file__).resolve().parent.parent

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.S)
EMBED = re.compile(r"!\[\[([^\]|#]+)(?:\|([^\]]*))?\]\]")
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
CALLOUT = re.compile(r"^(\s*>\s*)\[!(\w+)\][+-]?\s*(.*)$")


def frontmatter(text: str) -> dict:
    """Flat `key: value` frontmatter only, which is all a note needs."""
    m = FRONTMATTER.match(text)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "-")):
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def find_attachment(name: str, note: Path) -> Path | None:
    for candidate in (note.parent / name, note.parent / "assets" / name, VAULT / "assets" / name):
        if candidate.is_file():
            return candidate
    hits = [p for p in VAULT.rglob(name) if ".trash" not in p.parts]
    return hits[0] if hits else None


def convert(text: str, note: Path, bundle: Path, missing: list) -> str:
    text = FRONTMATTER.sub("", text, count=1)
    text = re.sub(r"%%.*?%%", "", text, flags=re.S)

    def embed(m):
        name, caption = m.group(1).strip(), (m.group(2) or "").strip()
        src = find_attachment(name, note)
        if not src:
            missing.append(name)
            return m.group(0)
        shutil.copy2(src, bundle / src.name)
        return f"![{'' if caption.isdigit() else caption}]({src.name})"

    out = []
    for line in text.splitlines():
        line = EMBED.sub(embed, line)
        line = WIKILINK.sub(lambda m: (m.group(2) or m.group(1)).strip(), line)
        c = CALLOUT.match(line)
        if c:
            line = f"{c.group(1)}**{c.group(3).strip() or c.group(2).capitalize()}**"
        out.append(line)
    body = "\n".join(out).strip()
    # A leading "# Title" duplicates the page title.
    body = re.sub(r"\A#\s+[^\n]*\n+", "", body)
    return body + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("note", type=Path)
    ap.add_argument("--section", required=True, choices=["thoughts", "writings"])
    ap.add_argument("--slug")
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()

    note = args.note.resolve()
    if not note.is_file():
        sys.exit(f"no such note: {note}")
    text = note.read_text()
    meta = frontmatter(text)
    heading = re.search(r"^#\s+(.+)$", FRONTMATTER.sub("", text, count=1), re.M)
    title = meta.get("title") or (heading.group(1).strip() if heading else note.stem)
    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    bundle = SITE / "content" / args.section / slug
    bundle.mkdir(parents=True, exist_ok=True)
    index = bundle / "index.md"
    old = frontmatter(index.read_text()) if index.is_file() else {}

    missing: list = []
    body = convert(text, note, bundle, missing)
    date = dt.date.today().isoformat() if args.publish else old.get("date", dt.date.today().isoformat())
    draft = "false" if args.publish else old.get("draft", "true")

    head = ["---", f"title: {json.dumps(title, ensure_ascii=False)}", f"date: {date}", f"draft: {draft}"]
    tags = [t.strip().strip('"\'') for t in meta.get("tags", "").strip("[]").split(",") if t.strip()]
    tags = tags or [t for t in old.get("tags", "").strip("[]").replace('"', "").split(", ") if t]
    if tags:
        head.append(f"tags: {json.dumps(tags, ensure_ascii=False)}")
    for key in ("description", "canonical"):
        value = meta.get(key) or old.get(key, "").strip('"')
        if value:
            head.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    head.append("---")
    index.write_text("\n".join(head) + "\n\n" + body)

    words = len(re.findall(r"\w+", body))
    print(f"{index.relative_to(SITE)}: {words} words — {'PUBLISH' if draft == 'false' else 'draft'}")
    if missing:
        print("attachments not found in the vault: " + ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
