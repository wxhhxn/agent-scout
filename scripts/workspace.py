#!/usr/bin/env python3
"""Initialize and maintain an AgentScout local research workspace."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path


CONFIG = """# AgentScout Configuration

## Delivery
- Language: zh-CN
- Cadence: twice-weekly
- Items per digest: 5
- Summary depth: technical

## Scope
- Topics: memory, planning, tool use, computer use, evaluation, safety, multi-agent systems, agent infrastructure
- Content types: technical reports, papers, engineering posts, official repositories
- Companies: unrestricted
- Lookback: since last run; otherwise 14 days

## Recommendation Mix
- Recent-interest match: 70%
- Adjacent: 20%
- Exploration: 10%

## Source Policy
- Prefer primary sources: true
- Allow secondary sources: for context only
- Require canonical URL: true

## Exclusions
- Marketing-only announcements
- Unsourced reposts
"""

MEMORY = """# AgentScout Memory

Updated: {today}
Evidence window: not enough archive history yet

## Stable interests

## Recent strong signals

## Emerging interests

## Fading interests

## Negative preferences

## Open questions

## Promising continuation directions

## Recommendation policy
- Match / adjacent / exploration: 70 / 20 / 10
"""


def ensure_within(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    if candidate != root and root not in candidate.parents:
        raise SystemExit(f"Path escapes research root: {candidate}")
    return candidate


def init_workspace(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for relative in ("inbox", "archive", "reports", "state"):
        (root / relative).mkdir(exist_ok=True)
    config = root / "config.md"
    memory = root / "memory.md"
    seen = root / "state" / "seen.jsonl"
    index = root / "archive-index.md"
    if not config.exists():
        config.write_text(CONFIG, encoding="utf-8")
    if not memory.exists():
        memory.write_text(MEMORY.format(today=date.today().isoformat()), encoding="utf-8")
    seen.touch(exist_ok=True)
    if not index.exists():
        index.write_text("# AgentScout Archive Index\n", encoding="utf-8")
    print(root.resolve())


def digest_items(text: str) -> list[dict[str, str]]:
    keys = re.findall(r"^##\s+(AS-\d{8}-\d+)\s+—\s+(.+)$", text, re.MULTILINE)
    blocks = re.split(r"^##\s+AS-\d{8}-\d+\s+—\s+.+$", text, flags=re.MULTILINE)[1:]
    result = []
    for (key, title), block in zip(keys, blocks):
        match = re.search(r"^- Link:\s+(\S+)", block, re.MULTILINE)
        if match:
            result.append({"key": key, "title": title.strip(), "url": match.group(1)})
    return result


def mark_seen(root: Path, digest: Path) -> None:
    digest = ensure_within(root, digest)
    items = digest_items(digest.read_text(encoding="utf-8"))
    target = root.resolve() / "state" / "seen.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    delivered = datetime.now(timezone.utc).isoformat()
    with target.open("a", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps({**item, "delivered_at": delivered}, ensure_ascii=False) + "\n")
    print(f"recorded {len(items)} items")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    data = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data


def rebuild_index(root: Path) -> None:
    archive = root.resolve() / "archive"
    rows = []
    for path in sorted(archive.rglob("*.md")) if archive.exists() else []:
        meta = frontmatter(path)
        title = meta.get("title", path.stem)
        archived = meta.get("archived_at", "unknown")[:10]
        source = meta.get("source", "unknown")
        digest_key = meta.get("digest_key", "unkeyed")
        article_type = meta.get("article_type", "not classified")
        central_claim = meta.get("central_claim", "Not recorded.")
        evidence_level = meta.get("evidence_level", "not rated")
        resolution_status = meta.get("resolution_status", "not rated")
        summary = meta.get("summary", "No summary recorded.")
        canonical = meta.get("canonical_url", "")
        relative = path.relative_to(root.resolve()).as_posix()
        source_line = f"- Original source: {canonical}" if canonical else "- Original source: not recorded"
        rows.append(
            f"## {digest_key} — {title}\n\n"
            f"- Archived: {archived}\n"
            f"- Publisher / authors: {source}\n"
            f"- Article type: {article_type}\n"
            f"- Evidence maturity: {evidence_level}\n"
            f"- Resolution status: {resolution_status}\n"
            f"- Local article: [{relative}]({relative})\n"
            f"{source_line}\n"
            f"- Central claim: {central_claim}\n"
            f"- Summary: {summary}"
        )
    content = "# AgentScout Archive Index\n\n" + ("\n\n".join(rows) if rows else "No archived items yet.") + "\n"
    (root.resolve() / "archive-index.md").write_text(content, encoding="utf-8")
    print(f"indexed {len(rows)} items")


def open_index(root: Path, print_only: bool = False) -> None:
    index = ensure_within(root, root.resolve() / "archive-index.md")
    if not index.is_file():
        raise SystemExit(f"Archive index does not exist: {index}")
    if print_only:
        print(index)
        return
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", str(index)], check=True)
    elif system == "Windows":
        os.startfile(index)  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", str(index)], check=True)
    print(index)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    init_cmd = sub.add_parser("init")
    init_cmd.add_argument("root", type=Path)
    seen_cmd = sub.add_parser("seen")
    seen_cmd.add_argument("root", type=Path)
    seen_cmd.add_argument("--digest", required=True, type=Path)
    index_cmd = sub.add_parser("index")
    index_cmd.add_argument("root", type=Path)
    open_cmd = sub.add_parser("open-index")
    open_cmd.add_argument("root", type=Path)
    open_cmd.add_argument("--print-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "init":
        init_workspace(root)
    elif args.command == "seen":
        mark_seen(root, args.digest)
    elif args.command == "index":
        rebuild_index(root)
    elif args.command == "open-index":
        open_index(root, args.print_only)


if __name__ == "__main__":
    main()
