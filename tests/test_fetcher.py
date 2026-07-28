"""Tests for bskysnap.fetcher."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import click

from bskysnap.fetcher import (
    BskyPost,
    BskyProfile,
    _rkey_from_uri,
    normalize_handle,
    get_author_feed,
)


class TestNormalizeHandle:
    def test_short_handle_gets_suffix(self):
        assert normalize_handle("swyx") == "swyx.bsky.social"

    def test_dotted_handle_unchanged(self):
        assert normalize_handle("bsky.app") == "bsky.app"

    def test_full_bsky_social_handle_unchanged(self):
        assert normalize_handle("user.bsky.social") == "user.bsky.social"

    def test_custom_domain_unchanged(self):
        assert normalize_handle("atproto.com") == "atproto.com"


class TestRkeyFromUri:
    def test_extracts_rkey(self):
        uri = "at://did:plc:abc123/app.bsky.feed.post/3mqc36slinc2m"
        assert _rkey_from_uri(uri) == "3mqc36slinc2m"

    def test_handles_short_rkey(self):
        uri = "at://did:plc:abc/app.bsky.feed.post/rkey"
        assert _rkey_from_uri(uri) == "rkey"


class TestGetAuthorFeed:
    def _make_feed_item(self, text="Hello", is_repost=False):
        item = {
            "post": {
                "uri": "at://did:plc:abc123/app.bsky.feed.post/rkey001",
                "author": {
                    "handle": "bsky.app",
                    "displayName": "Bluesky",
                },
                "record": {
                    "text": text,
                    "createdAt": "2026-07-10T17:43:30.000Z",
                },
                "likeCount": 42,
                "replyCount": 5,
                "repostCount": 10,
            }
        }
        if is_repost:
            item["reason"] = {
                "$type": "app.bsky.feed.defs#reasonRepost",
            }
        return item

    def _make_profile_response(self):
        return {
            "handle": "bsky.app",
            "displayName": "Bluesky",
            "description": "The Bluesky social network.",
            "followersCount": 100000,
            "postsCount": 200,
        }

    @patch("bskysnap.fetcher.httpx.get")
    def test_returns_profile_and_posts(self, mock_get):
        mock_profile_resp = MagicMock()
        mock_profile_resp.status_code = 200
        mock_profile_resp.json.return_value = self._make_profile_response()

        mock_feed_resp = MagicMock()
        mock_feed_resp.status_code = 200
        mock_feed_resp.json.return_value = {
            "feed": [self._make_feed_item("Post 1"), self._make_feed_item("Post 2")]
        }

        mock_get.side_effect = [mock_profile_resp, mock_feed_resp]

        profile, posts = get_author_feed("bsky.app", limit=2)

        assert isinstance(profile, BskyProfile)
        assert profile.handle == "bsky.app"
        assert isinstance(posts, list)
        assert len(posts) == 2
        assert posts[0].text == "Post 1"

    @patch("bskysnap.fetcher.httpx.get")
    def test_excludes_reposts_when_flag_set(self, mock_get):
        mock_profile_resp = MagicMock()
        mock_profile_resp.status_code = 200
        mock_profile_resp.json.return_value = self._make_profile_response()

        mock_feed_resp = MagicMock()
        mock_feed_resp.status_code = 200
        mock_feed_resp.json.return_value = {
            "feed": [
                self._make_feed_item("Original"),
                self._make_feed_item("Reposted", is_repost=True),
            ]
        }

        mock_get.side_effect = [mock_profile_resp, mock_feed_resp]

        _, posts = get_author_feed("bsky.app", limit=10, include_reposts=False)

        assert all(not p.is_repost for p in posts)
        assert len(posts) == 1
        assert posts[0].text == "Original"

    @patch("bskysnap.fetcher.httpx.get")
    def test_404_raises_click_exception(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_get.return_value = mock_resp

        with pytest.raises(click.ClickException) as exc_info:
            get_author_feed("nonexistent.bsky.social")

        assert "not found" in str(exc_info.value.format_message()).lower()

    @patch("bskysnap.fetcher.httpx.get")
    def test_empty_feed_returns_empty_list(self, mock_get):
        mock_profile_resp = MagicMock()
        mock_profile_resp.status_code = 200
        mock_profile_resp.json.return_value = self._make_profile_response()

        mock_feed_resp = MagicMock()
        mock_feed_resp.status_code = 200
        mock_feed_resp.json.return_value = {"feed": []}

        mock_get.side_effect = [mock_profile_resp, mock_feed_resp]

        profile, posts = get_author_feed("bsky.app")
        assert posts == []

    @patch("bskysnap.fetcher.httpx.get")
    def test_respects_limit(self, mock_get):
        mock_profile_resp = MagicMock()
        mock_profile_resp.status_code = 200
        mock_profile_resp.json.return_value = self._make_profile_response()

        mock_feed_resp = MagicMock()
        mock_feed_resp.status_code = 200
        mock_feed_resp.json.return_value = {
            "feed": [self._make_feed_item(f"Post {i}") for i in range(20)]
        }

        mock_get.side_effect = [mock_profile_resp, mock_feed_resp]

        _, posts = get_author_feed("bsky.app", limit=3)
        assert len(posts) == 3
