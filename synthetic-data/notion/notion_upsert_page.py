#!/usr/bin/env python3
"""
Upload a Markdown file to a Notion page.

Usage:
  export NOTION_TOKEN="ntn_xxx"          # never paste the token in chat or code
  python3 notion_upsert_page.py --page-id YOUR_32_CHAR_PAGE_ID --file guide.md

If --page-id is omitted, a new page is created at the workspace root
(requires the integration to have workspace-level access).
"""
import argparse, os, sys
from pathlib import Path

import requests

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def md_to_blocks(md: str):
    """Minimal Markdown -> Notion blocks converter (headings, bullets, paragraphs)."""
    blocks = []
    for line in md.splitlines():
        s = line.rstrip()
        if not s.strip():
            continue
        if s.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3",
                           "heading_3": {"rich_text": [{"type": "text", "text": {"content": s[4:].strip()}}]}})
        elif s.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2",
                           "heading_2": {"rich_text": [{"type": "text", "text": {"content": s[3:].strip()}}]}})
        elif s.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1",
                           "heading_1": {"rich_text": [{"type": "text", "text": {"content": s[2:].strip()}}]}})
        elif s.lstrip().startswith("- "):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                           "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": s.lstrip()[2:].strip()}}]}})
        else:
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": [{"type": "text", "text": {"content": s}}]}})
    return blocks


def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }


def append_blocks(token, page_id, blocks):
    # Notion allows max 100 children per request
    for i in range(0, len(blocks), 100):
        chunk = blocks[i:i + 100]
        r = requests.patch(f"{NOTION_API}/blocks/{page_id}/children",
                           headers=headers(token), json={"children": chunk})
        if r.status_code != 200:
            print(f"ERROR {r.status_code}: {r.text}", file=sys.stderr)
            sys.exit(1)


def create_page(token, title, blocks):
    payload = {
        "parent": {"type": "workspace", "workspace": True},
        "properties": {"title": {"title": [{"type": "text", "text": {"content": title}}]}},
        "children": blocks[:100],
    }
    r = requests.post(f"{NOTION_API}/pages", headers=headers(token), json=payload)
    if r.status_code != 200:
        print(f"ERROR {r.status_code}: {r.text}", file=sys.stderr)
        sys.exit(1)
    page = r.json()
    if len(blocks) > 100:
        append_blocks(token, page["id"], blocks[100:])
    return page


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--page-id", default=None, help="Existing Notion page ID to append to")
    p.add_argument("--title", default="Synthetic Data Guide", help="Title when creating a new page")
    p.add_argument("--file", required=True, help="Markdown file to upload")
    args = p.parse_args()

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("ERROR: set NOTION_TOKEN env var first.", file=sys.stderr)
        sys.exit(1)

    md = Path(args.file).read_text(encoding="utf-8")
    blocks = md_to_blocks(md)
    print(f"Converted {len(blocks)} blocks from {args.file}")

    if args.page_id:
        append_blocks(token, args.page_id, blocks)
        print(f"Appended blocks to page: {args.page_id}")
    else:
        page = create_page(token, args.title, blocks)
        print(f"Created page: {page.get('url', page.get('id'))}")


if __name__ == "__main__":
    main()
