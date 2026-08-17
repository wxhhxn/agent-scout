from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "workspace.py"
SPEC = importlib.util.spec_from_file_location("agent_scout_workspace", SCRIPT)
assert SPEC and SPEC.loader
workspace = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workspace)


VALID_ARCHIVE = """---
title: "Example Agent Report"
canonical_url: "https://example.com/report"
source: "Example Lab"
published_at: "2026-08-01"
archived_at: "2026-08-17T10:00:00+08:00"
digest_key: "AS-20260817-01"
article_type: "research-paper"
central_claim: "The report demonstrates a testable claim."
evidence_level: "controlled-experiment"
resolution_status: "partial"
summary: "A concise technical summary."
tags: [agent, evaluation]
---

# Example Agent Report
"""

DIGEST = """# AgentScout Digest

## AS-20260817-01 — First work

- Link: https://example.com/one/

## AS-20260817-02 - Second work

- Link: https://example.com/two
"""


class WorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "research"
        self.registry = self.base / "agent-scout.json"
        self.env = mock.patch.dict(os.environ, {workspace.REGISTRY_ENV: str(self.registry)})
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()
        self.temp.cleanup()

    def test_init_registers_workspace_and_is_idempotent(self) -> None:
        workspace.init_workspace(self.root)
        custom = "# My configuration\n"
        (self.root / "config.md").write_text(custom, encoding="utf-8")

        workspace.init_workspace(self.root)

        self.assertEqual((self.root / "config.md").read_text(encoding="utf-8"), custom)
        self.assertEqual(workspace.registered_root(), self.root.resolve())
        self.assertEqual(json.loads(self.registry.read_text())["research_root"], str(self.root.resolve()))

    def test_registered_root_reports_missing_registry(self) -> None:
        with self.assertRaisesRegex(workspace.WorkspaceError, "No AgentScout research workspace"):
            workspace.registered_root()

    def test_registered_root_rejects_invalid_registry(self) -> None:
        self.registry.write_text("not-json", encoding="utf-8")
        with self.assertRaisesRegex(workspace.WorkspaceError, "Invalid AgentScout registry"):
            workspace.registered_root()

    def test_digest_parser_accepts_dash_variants(self) -> None:
        self.assertEqual(
            workspace.digest_items(DIGEST),
            [
                {"key": "AS-20260817-01", "title": "First work", "url": "https://example.com/one/"},
                {"key": "AS-20260817-02", "title": "Second work", "url": "https://example.com/two"},
            ],
        )

    def test_digest_parser_rejects_missing_link(self) -> None:
        with self.assertRaises(workspace.WorkspaceError):
            workspace.digest_items("## AS-20260817-01 — Missing link\n")

    def test_seen_is_idempotent_by_key_and_canonical_url(self) -> None:
        workspace.init_workspace(self.root)
        digest = self.root / "inbox" / "digest.md"
        digest.write_text(DIGEST, encoding="utf-8")

        workspace.mark_seen(self.root, digest)
        workspace.mark_seen(self.root, digest)

        lines = (self.root / "state" / "seen.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)

    def test_seen_rejects_digest_outside_workspace(self) -> None:
        workspace.init_workspace(self.root)
        outside = self.base / "outside.md"
        outside.write_text(DIGEST, encoding="utf-8")
        with self.assertRaises(workspace.WorkspaceError):
            workspace.mark_seen(self.root, outside)

    def test_rebuild_index_validates_and_indexes_archive(self) -> None:
        workspace.init_workspace(self.root)
        article = self.root / "archive" / "2026" / "example.md"
        article.parent.mkdir()
        article.write_text(VALID_ARCHIVE, encoding="utf-8")

        workspace.rebuild_index(self.root)

        index = (self.root / "archive-index.md").read_text(encoding="utf-8")
        self.assertIn("AS-20260817-01", index)
        self.assertIn("archive/2026/example.md", index)
        self.assertIn("https://example.com/report", index)

    def test_rebuild_index_rejects_missing_frontmatter_field(self) -> None:
        workspace.init_workspace(self.root)
        article = self.root / "archive" / "broken.md"
        article.write_text(VALID_ARCHIVE.replace('summary: "A concise technical summary."\n', ""), encoding="utf-8")
        with self.assertRaisesRegex(workspace.WorkspaceError, "summary"):
            workspace.rebuild_index(self.root)

    def test_rebuild_index_rejects_invalid_frontmatter(self) -> None:
        workspace.init_workspace(self.root)
        article = self.root / "archive" / "broken.md"
        article.write_text(VALID_ARCHIVE.replace('article_type: "research-paper"', 'article_type: "unknown"'), encoding="utf-8")
        with self.assertRaisesRegex(workspace.WorkspaceError, "article_type"):
            workspace.rebuild_index(self.root)

    def test_open_index_print_only(self) -> None:
        workspace.init_workspace(self.root)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            workspace.open_index(self.root, print_only=True)
        self.assertIn(str(self.root / "archive-index.md"), output.getvalue())

    def test_open_index_uses_platform_viewer(self) -> None:
        workspace.init_workspace(self.root)
        index_path = (self.root / "archive-index.md").resolve()
        index = str(index_path)
        with mock.patch.object(workspace.platform, "system", return_value="Darwin"), mock.patch.object(
            workspace.subprocess, "run"
        ) as run:
            workspace.open_index(self.root)
            run.assert_called_once_with(["open", index], check=True)
        with mock.patch.object(workspace.platform, "system", return_value="Linux"), mock.patch.object(
            workspace.subprocess, "run"
        ) as run:
            workspace.open_index(self.root)
            run.assert_called_once_with(["xdg-open", index], check=True)
        with mock.patch.object(workspace.platform, "system", return_value="Windows"), mock.patch.object(
            workspace.os, "startfile", create=True
        ) as startfile:
            workspace.open_index(self.root)
            startfile.assert_called_once_with(index_path)


if __name__ == "__main__":
    unittest.main()
