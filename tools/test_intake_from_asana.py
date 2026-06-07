#!/usr/bin/env python3
"""Tests for intake_from_asana requester_comments."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import intake_from_asana as ifa  # noqa: E402


class RequesterCommentTests(unittest.TestCase):
    def test_filters_by_assignee(self) -> None:
        task = {"assignee": {"name": "Alice", "gid": "U1"}}
        comments = [
            {"author": "Alice", "author_gid": "U1", "text": "please do X"},
            {"author": "Bob", "author_gid": "U2", "text": "noise"},
        ]
        matched = ifa.extract_requester_comments(task, comments)
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0]["text"], "please do X")

    def test_build_snapshot_includes_requester_comments(self) -> None:
        task = {
            "gid": "T1",
            "assignee": {"name": "Alice", "gid": "U1"},
            "parent": {},
        }
        comments = [{"author": "Alice", "author_gid": "U1", "text": "go", "created_at": ""}]
        snap = ifa.build_snapshot(task, comments)
        self.assertEqual(snap["schema_version"], "1.2")
        self.assertEqual(len(snap["requester_comments"]), 1)


if __name__ == "__main__":
    unittest.main()
