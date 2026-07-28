"""Tests for bskysnap.cli."""

import json
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from bskysnap.cli import main
from bskysnap.fetcher import BskyPost, BskyProfile


def _make_profile():
    return BskyProfile(
        handle="bsky.app",
        display_name="Bluesky",
        description="Social networking.",
        followers_count=100000,
        posts_count=200,
    )


def _make_posts(n=2):
    return [
        BskyPost(
            uri=f"at://did:plc:abc/app.bsky.feed.post/rkey{i:03}",
            handle="bsky.app",
            display_name="Bluesky",
            text=f"Post number {i}",
            created_at=datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc),
            like_count=i * 10,
            reply_count=i,
            repost_count=i * 2,
            is_repost=False,
            web_url=f"https://bsky.app/profile/bsky.app/post/rkey{i:03}",
        )
        for i in range(1, n + 1)
    ]


class TestCli:
    def test_help_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Bluesky" in result.output or "markdown" in result.output

    def test_no_args_exits_one(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 1

    def test_introspect_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["introspect"])
        assert result.exit_code == 0

    def test_introspect_returns_valid_json(self):
        runner = CliRunner()
        result = runner.invoke(main, ["introspect"])
        data = json.loads(result.output)
        assert data["tool"] == "bskysnap"

    def test_skill_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["skill"])
        assert result.exit_code == 0

    def test_skill_contains_tool_name(self):
        runner = CliRunner()
        result = runner.invoke(main, ["skill"])
        assert "bskysnap" in result.output

    @patch("bskysnap.cli.get_author_feed")
    def test_default_text_output(self, mock_feed):
        mock_feed.return_value = (_make_profile(), _make_posts())
        runner = CliRunner()
        result = runner.invoke(main, ["bsky.app"])
        assert result.exit_code == 0
        assert "@bsky.app" in result.output or "Post number" in result.output

    @patch("bskysnap.cli.get_author_feed")
    def test_json_output(self, mock_feed):
        mock_feed.return_value = (_make_profile(), _make_posts())
        runner = CliRunner()
        result = runner.invoke(main, ["bsky.app", "--output", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["tool"] == "bskysnap"

    @patch("bskysnap.cli.get_author_feed")
    def test_table_output(self, mock_feed):
        mock_feed.return_value = (_make_profile(), _make_posts())
        runner = CliRunner()
        result = runner.invoke(main, ["bsky.app", "--output", "table"])
        assert result.exit_code == 0
        assert "date" in result.output

    @patch("bskysnap.cli.get_author_feed")
    def test_csv_output_has_header(self, mock_feed):
        mock_feed.return_value = (_make_profile(), _make_posts())
        runner = CliRunner()
        result = runner.invoke(main, ["bsky.app", "--output", "csv"])
        assert result.exit_code == 0
        first_line = result.output.strip().splitlines()[0]
        assert "date" in first_line
        assert "text" in first_line
