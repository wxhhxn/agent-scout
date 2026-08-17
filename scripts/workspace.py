#!/usr/bin/env python3
"""Initialize, locate, and maintain an AgentScout research workspace."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


REGISTRY_ENV = "AGENT_SCOUT_REGISTRY"
REQUIRED_ARCHIVE_FIELDS = (
    "title",
    "canonical_url",
    "source",
    "published_at",
    "archived_at",
    "digest_key",
    "article_type",
    "central_claim",
    "evidence_level",
    "resolution_status",
    "summary",
    "tags",
)
ALLOWED_ARTICLE_TYPES = {
    "research-paper",
    "system-design",
    "model-report",
    "benchmark-evaluation",
    "security-incident",
    "industry-practice",
}
ALLOWED_EVIDENCE_LEVELS = {
    "problem-observed",
    "prototype",
    "controlled-experiment",
    "cross-setting-validation",
    "real-world-evidence",
    "production-longitudinal",
}
ALLOWED_RESOLUTION_STATUSES = {"unresolved", "partial", "substantial", "unclear"}


CONFIG = """# AgentScout Configuration

## Delivery
- Language: zh-CN
- Cadence: twice-weekly
- Items per digest: 5
- Summary depth: technical

## Scope
- Topics: memory, planning, tool use, computer use, evaluation, safety, multi-agent systems, agent infrastructure
- Content types: technical reports, papers, engineering posts, official repositories
- Lookback: since last successful run; otherwise 14 completed calendar days ending yesterday
- Retrospective windows: adjacent, with no overlap or gaps

## Source Lanes
- Industrial AI labs: 60%
- Academic research: 25%
- Open-source community: 15%

## Priority Organizations
- OpenAI
- Google DeepMind
- DeepSeek
- Zhipu AI / GLM
- Anthropic
- Meta AI
- Microsoft Research
- Alibaba
- ByteDance

## Recommendation Mix
- Recent-interest match: 70%
- Adjacent: 20%
- Exploration: 10%

## Source Policy
- Prefer primary sources: true
- Allow secondary sources: for context only
- Require canonical URL: true
- Organization prominence affects coverage, not ranking score: true

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


class WorkspaceError(RuntimeError):
    """A user-actionable AgentScout workspace error."""


def registry_path() -> Path:
    override = os.environ.get(REGISTRY_ENV)
    return Path(override).expanduser() if override else Path.home() / ".codex" / "agent-scout.json"


def write_registry(root: Path) -> Path:
    target = registry_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps({"research_root": str(root.resolve())}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)
    return target


def registered_root() -> Path:
    target = registry_path()
    if not target.is_file():
        raise WorkspaceError(
            "No AgentScout research workspace is registered. "
            "Run `python3 scripts/workspace.py init <root>` once."
        )
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkspaceError(f"Invalid AgentScout registry {target}: {exc}") from exc
    value = data.get("research_root") if isinstance(data, dict) else None
    if not isinstance(value, str) or not value.strip():
        raise WorkspaceError(f"Registry {target} does not contain a valid research_root.")
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise WorkspaceError(f"Registered research workspace does not exist: {root}")
    return root


def resolve_root(explicit: Path | None) -> Path:
    return explicit.expanduser().resolve() if explicit is not None else registered_root()


def ensure_within(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    if candidate != root and root not in candidate.parents:
        raise WorkspaceError(f"Path escapes research root: {candidate}")
    return candidate


def init_workspace(root: Path) -> None:
    root = root.expanduser().resolve()
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
    registry = write_registry(root)
    print(f"workspace: {root}")
    print(f"registry: {registry}")


def digest_items(text: str) -> list[dict[str, str]]:
    heading = re.compile(r"^##\s+(AS-\d{8}-\d+)\s+(?:—|-)\s+(.+?)\s*$", re.MULTILINE)
    matches = list(heading.finditer(text))
    if not matches:
        raise WorkspaceError("Digest contains no AgentScout item headings.")
    result: list[dict[str, str]] = []
    keys: set[str] = set()
    for position, match in enumerate(matches):
        key, title = match.group(1), match.group(2).strip()
        if key in keys:
            raise WorkspaceError(f"Digest contains duplicate archive key: {key}")
        keys.add(key)
        end = matches[position + 1].start() if position + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        link = re.search(r"^-\s*Link:\s*(https?://\S+)\s*$", block, re.MULTILINE | re.IGNORECASE)
        if not link:
            raise WorkspaceError(f"Digest item {key} has no valid HTTP(S) Link field.")
        result.append({"key": key, "title": title, "url": link.group(1)})
    return result


def canonicalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/") or "/", parts.query, ""))


def read_seen(target: Path) -> tuple[set[str], set[str]]:
    keys: set[str] = set()
    urls: set[str] = set()
    if not target.exists():
        return keys, urls
    for number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise WorkspaceError(f"Invalid JSON in {target} line {number}: {exc}") from exc
        if isinstance(item.get("key"), str):
            keys.add(item["key"])
        if isinstance(item.get("url"), str):
            urls.add(canonicalize_url(item["url"]))
    return keys, urls


def mark_seen(root: Path, digest: Path) -> None:
    digest = ensure_within(root, digest)
    items = digest_items(digest.read_text(encoding="utf-8"))
    target = root.resolve() / "state" / "seen.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    known_keys, known_urls = read_seen(target)
    delivered = datetime.now(timezone.utc).isoformat()
    added = 0
    with target.open("a", encoding="utf-8") as handle:
        for item in items:
            normalized = canonicalize_url(item["url"])
            if item["key"] in known_keys or normalized in known_urls:
                continue
            handle.write(json.dumps({**item, "delivered_at": delivered}, ensure_ascii=False) + "\n")
            known_keys.add(item["key"])
            known_urls.add(normalized)
            added += 1
    print(f"recorded {added} new items; skipped {len(items) - added} duplicates")


def parse_scalar(raw: str, path: Path, line_number: int) -> str:
    value = raw.strip()
    if not value:
        raise WorkspaceError(f"Empty frontmatter value in {path} line {line_number}.")
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise WorkspaceError(f"Invalid quoted value in {path} line {line_number}: {exc}") from exc
        if not isinstance(parsed, str):
            raise WorkspaceError(f"Expected a string in {path} line {line_number}.")
        return parsed
    if value.startswith("'"):
        if not value.endswith("'"):
            raise WorkspaceError(f"Unclosed quoted value in {path} line {line_number}.")
        return value[1:-1].replace("''", "'")
    return value


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise WorkspaceError(f"Archive file has no YAML frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise WorkspaceError(f"Archive file has unclosed YAML frontmatter: {path}")
    data: dict[str, str] = {}
    for line_number, line in enumerate(text[4:end].splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise WorkspaceError(f"Unsupported frontmatter syntax in {path} line {line_number}: {line}")
        key, raw = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise WorkspaceError(f"Invalid frontmatter key in {path} line {line_number}: {key}")
        if key in data:
            raise WorkspaceError(f"Duplicate frontmatter key in {path}: {key}")
        data[key] = parse_scalar(raw, path, line_number)
    missing = [field for field in REQUIRED_ARCHIVE_FIELDS if not data.get(field)]
    if missing:
        raise WorkspaceError(f"Archive file {path} is missing required frontmatter: {', '.join(missing)}")
    if data["article_type"] not in ALLOWED_ARTICLE_TYPES:
        raise WorkspaceError(f"Invalid article_type in {path}: {data['article_type']}")
    if data["evidence_level"] not in ALLOWED_EVIDENCE_LEVELS:
        raise WorkspaceError(f"Invalid evidence_level in {path}: {data['evidence_level']}")
    if data["resolution_status"] not in ALLOWED_RESOLUTION_STATUSES:
        raise WorkspaceError(f"Invalid resolution_status in {path}: {data['resolution_status']}")
    if not re.fullmatch(r"AS-\d{8}-\d+", data["digest_key"]):
        raise WorkspaceError(f"Invalid digest_key in {path}: {data['digest_key']}")
    if not re.match(r"https?://", data["canonical_url"]):
        raise WorkspaceError(f"Invalid canonical_url in {path}: {data['canonical_url']}")
    try:
        date.fromisoformat(data["published_at"])
        datetime.fromisoformat(data["archived_at"])
    except ValueError as exc:
        raise WorkspaceError(f"Invalid publication or archive date in {path}: {exc}") from exc
    if not (data["tags"].startswith("[") and data["tags"].endswith("]")):
        raise WorkspaceError(f"Tags must use an inline YAML list in {path}: {data['tags']}")
    return data


def rebuild_index(root: Path) -> None:
    archive = root.resolve() / "archive"
    rows = []
    paths = sorted(archive.rglob("*.md")) if archive.exists() else []
    for path in paths:
        meta = frontmatter(path)
        relative = path.relative_to(root.resolve()).as_posix()
        rows.append(
            f"## {meta['digest_key']} — {meta['title']}\n\n"
            f"- Archived: {meta['archived_at'][:10]}\n"
            f"- Publisher / authors: {meta['source']}\n"
            f"- Article type: {meta['article_type']}\n"
            f"- Evidence maturity: {meta['evidence_level']}\n"
            f"- Resolution status: {meta['resolution_status']}\n"
            f"- Local article: [{relative}]({relative})\n"
            f"- Original source: {meta['canonical_url']}\n"
            f"- Central claim: {meta['central_claim']}\n"
            f"- Summary: {meta['summary']}"
        )
    content = "# AgentScout Archive Index\n\n" + ("\n\n".join(rows) if rows else "No archived items yet.") + "\n"
    (root.resolve() / "archive-index.md").write_text(content, encoding="utf-8")
    print(f"indexed {len(rows)} items")


def open_index(root: Path, print_only: bool = False) -> None:
    index = ensure_within(root, root.resolve() / "archive-index.md")
    if not index.is_file():
        raise WorkspaceError(f"Archive index does not exist: {index}")
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
    init_cmd = sub.add_parser("init", help="initialize and register a research workspace")
    init_cmd.add_argument("root", type=Path)
    root_cmd = sub.add_parser("resolve-root", help="print the registered research workspace")
    root_cmd.add_argument("root", nargs="?", type=Path)
    seen_cmd = sub.add_parser("seen", help="record delivered digest items")
    seen_cmd.add_argument("root", nargs="?", type=Path)
    seen_cmd.add_argument("--digest", required=True, type=Path)
    index_cmd = sub.add_parser("index", help="rebuild the archive index")
    index_cmd.add_argument("root", nargs="?", type=Path)
    open_cmd = sub.add_parser("open-index", help="open the archive index")
    open_cmd.add_argument("root", nargs="?", type=Path)
    open_cmd.add_argument("--print-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "init":
            init_workspace(args.root)
            return
        root = resolve_root(args.root)
        if args.command == "resolve-root":
            print(root)
        elif args.command == "seen":
            mark_seen(root, args.digest)
        elif args.command == "index":
            rebuild_index(root)
        elif args.command == "open-index":
            open_index(root, args.print_only)
    except WorkspaceError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
