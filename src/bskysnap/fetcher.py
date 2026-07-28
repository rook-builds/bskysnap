"""Fetch posts from Bluesky's public API — no authentication required."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import click
import httpx

BASE_URL = "https://public.api.bsky.app/xrpc"


@dataclass
class BskyPost:
    uri: str            # at://did:plc:.../app.bsky.feed.post/rkey
    handle: str         # author handle (e.g. bsky.app)
    display_name: str   # author display name
    text: str           # post text
    created_at: datetime  # UTC-aware
    like_count: int
    reply_count: int
    repost_count: int
    is_repost: bool     # True if this entry is a repost of someone else's post
    web_url: str        # https://bsky.app/profile/{handle}/post/{rkey}


@dataclass
class BskyProfile:
    handle: str
    display_name: str
    description: str
    followers_count: int
    posts_count: int


def normalize_handle(handle: str) -> str:
    """Append .bsky.social if the handle has no dots (shorthand support)."""
    if "." not in handle:
        return f"{handle}.bsky.social"
    return handle


def _rkey_from_uri(uri: str) -> str:
    """Extract the record key from an AT Protocol URI."""
    return uri.rsplit("/", 1)[-1]


def _parse_dt(s: str) -> datetime:
    """Parse an ISO 8601 datetime string to a UTC-aware datetime."""
    # Strip sub-second precision and Z suffix for fromisoformat compat
    s = re.sub(r"\.\d+Z$", "Z", s)
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)


def _parse_since(since: str) -> Optional[datetime]:
    """Parse a --since value: YYYY-MM-DD or Nd (e.g. 3d)."""
    if since is None:
        return None
    match = re.fullmatch(r"(\d+)d", since)
    if match:
        days = int(match.group(1))
        return datetime.now(tz=timezone.utc) - timedelta(days=days)
    # Try YYYY-MM-DD
    try:
        dt = datetime.strptime(since, "%Y-%m-%d")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        raise click.ClickException(
            f"Invalid --since value '{since}'. Use YYYY-MM-DD or Nd (e.g. 7d)."
        )


def _fetch_profile(handle: str) -> BskyProfile:
    url = f"{BASE_URL}/app.bsky.actor.getProfile"
    try:
        resp = httpx.get(url, params={"actor": handle}, timeout=10.0)
    except httpx.RequestError as exc:
        raise click.ClickException(f"Network error: {exc}") from exc

    if resp.status_code == 400 or resp.status_code == 404:
        raise click.ClickException(
            f"Handle '{handle}' not found. Check the spelling and try again."
        )
    resp.raise_for_status()
    data = resp.json()
    return BskyProfile(
        handle=data.get("handle", handle),
        display_name=data.get("displayName", handle),
        description=data.get("description", ""),
        followers_count=data.get("followersCount", 0),
        posts_count=data.get("postsCount", 0),
    )


def _fetch_feed_page(handle: str, limit: int) -> list[dict]:
    """Fetch a single page from getAuthorFeed."""
    url = f"{BASE_URL}/app.bsky.feed.getAuthorFeed"
    params = {
        "actor": handle,
        "limit": min(limit, 100),
        "filter": "posts_with_replies",
    }
    try:
        resp = httpx.get(url, params=params, timeout=10.0)
    except httpx.RequestError as exc:
        raise click.ClickException(f"Network error: {exc}") from exc

    if resp.status_code in (400, 404):
        raise click.ClickException(
            f"Handle '{handle}' not found. Check the spelling and try again."
        )
    resp.raise_for_status()
    return resp.json().get("feed", [])


def _item_to_post(item: dict) -> BskyPost:
    post = item["post"]
    record = post.get("record", {})
    author = post.get("author", {})
    handle = author.get("handle", "unknown")
    display_name = author.get("displayName", handle)
    uri = post.get("uri", "")
    rkey = _rkey_from_uri(uri)
    web_url = f"https://bsky.app/profile/{handle}/post/{rkey}"
    is_repost = "reason" in item and item["reason"] is not None
    created_at_str = record.get("createdAt", "")
    try:
        created_at = _parse_dt(created_at_str)
    except Exception:
        created_at = datetime(2000, 1, 1, tzinfo=timezone.utc)
    return BskyPost(
        uri=uri,
        handle=handle,
        display_name=display_name,
        text=record.get("text", ""),
        created_at=created_at,
        like_count=post.get("likeCount", 0),
        reply_count=post.get("replyCount", 0),
        repost_count=post.get("repostCount", 0),
        is_repost=is_repost,
        web_url=web_url,
    )


def get_author_feed(
    handle: str,
    limit: int = 10,
    include_reposts: bool = True,
    since: Optional[str] = None,
) -> tuple[BskyProfile, list[BskyPost]]:
    """Fetch profile and recent posts for a Bluesky handle.

    Returns:
        (profile, posts) where posts is filtered and limited.
    """
    handle = normalize_handle(handle)
    profile = _fetch_profile(handle)
    # Fetch more than needed so filters have room to work
    raw_items = _fetch_feed_page(handle, limit=max(limit * 3, 50))
    posts = [_item_to_post(item) for item in raw_items]

    # Apply --no-reposts filter
    if not include_reposts:
        posts = [p for p in posts if not p.is_repost]

    # Apply --since filter
    since_dt = _parse_since(since)
    if since_dt is not None:
        posts = [p for p in posts if p.created_at >= since_dt]

    return profile, posts[:limit]
