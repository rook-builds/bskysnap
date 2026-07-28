"""Format BskyPost lists into text, JSON, table, or CSV."""

from __future__ import annotations

import csv
import io
import json

from .fetcher import BskyPost, BskyProfile


def _fmt_dt(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def to_text(profile: BskyProfile, posts: list[BskyPost]) -> str:
    """Markdown digest of a Bluesky profile."""
    lines = [
        f"# Bluesky: @{profile.handle} ({profile.display_name})",
    ]
    if profile.description:
        for line in profile.description.splitlines():
            lines.append(f"> {line}")
    lines.append(f"> {profile.followers_count:,} followers")
    lines.append("")

    if not posts:
        lines.append("_No posts found._")
        return "\n".join(lines)

    for post in posts:
        lines.append("---")
        repost_tag = " 🔁 repost" if post.is_repost else ""
        lines.append(
            f"**{_fmt_dt(post.created_at)}**{repost_tag} "
            f"· {post.like_count} ❤️ · {post.reply_count} 💬 · {post.repost_count} 🔁"
        )
        # Quote the post text
        for text_line in post.text.splitlines():
            lines.append(f"> {text_line}")
        lines.append("")
        lines.append(f"[View post]({post.web_url})")
        lines.append("")

    return "\n".join(lines)


def to_json(profile: BskyProfile, posts: list[BskyPost]) -> str:
    """ACLI-compliant JSON envelope."""
    data = {
        "tool": "bskysnap",
        "version": "0.1.0",
        "handle": profile.handle,
        "display_name": profile.display_name,
        "followers_count": profile.followers_count,
        "posts": [
            {
                "uri": p.uri,
                "handle": p.handle,
                "display_name": p.display_name,
                "text": p.text,
                "created_at": p.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "like_count": p.like_count,
                "reply_count": p.reply_count,
                "repost_count": p.repost_count,
                "is_repost": p.is_repost,
                "web_url": p.web_url,
            }
            for p in posts
        ],
    }
    return json.dumps(data, indent=2)


def to_table(posts: list[BskyPost]) -> str:
    """Aligned column table for terminal scanning."""
    if not posts:
        return "No posts found."

    TEXT_WIDTH = 60
    header = f"{'date':<17}  {'likes':>6}  {'replies':>7}  {'reposts':>7}  text"
    sep = "-" * (17 + 2 + 6 + 2 + 7 + 2 + 7 + 2 + TEXT_WIDTH)
    rows = [header, sep]

    for p in posts:
        date_str = _fmt_dt(p.created_at)
        text_preview = p.text.replace("\n", " ")
        if len(text_preview) > TEXT_WIDTH:
            text_preview = text_preview[:TEXT_WIDTH - 1] + "…"
        repost_mark = "↩" if p.is_repost else " "
        rows.append(
            f"{date_str:<17}{repost_mark} "
            f"{p.like_count:>6}  "
            f"{p.reply_count:>7}  "
            f"{p.repost_count:>7}  "
            f"{text_preview}"
        )

    return "\n".join(rows)


def to_csv(posts: list[BskyPost]) -> str:
    """RFC 4180 CSV output."""
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL)
    writer.writerow(["date", "likes", "replies", "reposts", "is_repost", "handle", "text", "url"])
    for p in posts:
        writer.writerow([
            _fmt_dt(p.created_at),
            p.like_count,
            p.reply_count,
            p.repost_count,
            p.is_repost,
            p.handle,
            p.text,
            p.web_url,
        ])
    return buf.getvalue()
