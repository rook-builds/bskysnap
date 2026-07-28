"""Shared fixtures for bskysnap tests."""

from datetime import datetime, timezone

import pytest

from bskysnap.fetcher import BskyPost, BskyProfile


@pytest.fixture
def sample_profile():
    return BskyProfile(
        handle="bsky.app",
        display_name="Bluesky",
        description="The social network built on AT Protocol.",
        followers_count=119916,
        posts_count=232,
    )


@pytest.fixture
def sample_posts():
    return [
        BskyPost(
            uri="at://did:plc:abc123/app.bsky.feed.post/rkey001",
            handle="bsky.app",
            display_name="Bluesky",
            text="Hello from Bluesky!",
            created_at=datetime(2026, 7, 10, 17, 43, 30, tzinfo=timezone.utc),
            like_count=42,
            reply_count=5,
            repost_count=10,
            is_repost=False,
            web_url="https://bsky.app/profile/bsky.app/post/rkey001",
        ),
        BskyPost(
            uri="at://did:plc:def456/app.bsky.feed.post/rkey002",
            handle="someone.bsky.social",
            display_name="Someone",
            text="A reposted post, with commas, and \"quotes\".",
            created_at=datetime(2026, 7, 9, 12, 0, 0, tzinfo=timezone.utc),
            like_count=100,
            reply_count=20,
            repost_count=50,
            is_repost=True,
            web_url="https://bsky.app/profile/someone.bsky.social/post/rkey002",
        ),
    ]


@pytest.fixture
def empty_posts():
    return []
