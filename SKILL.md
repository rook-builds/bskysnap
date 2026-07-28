---
name: bskysnap
description: Fetch posts from any public Bluesky profile and format them as markdown, JSON, table, or CSV. Use when you need to monitor a Bluesky account, summarize recent posts, or pipe social content into an agent workflow. No authentication required.
license: MIT
metadata:
  author: rook-builds
  version: 0.1.0
---

## Core usage

```
bskysnap <handle>               # Markdown digest (default)
bskysnap <handle> -n 20         # Fetch 20 posts
bskysnap <handle> -o json       # JSON envelope for agent pipelines
bskysnap <handle> -o table      # Terminal-friendly table
bskysnap <handle> -o csv        # CSV for spreadsheets
bskysnap <handle> --since 7d    # Posts from last 7 days
bskysnap <handle> --no-reposts  # Exclude reposts
```

Short handles work too: `bskysnap swyx` → fetches `swyx.bsky.social`.

## Output modes

- `text` (default): human/LLM-readable markdown with post text, engagement counts (likes, replies, reposts), timestamps, and direct links
- `json`: ACLI envelope with structured post objects (uri, text, created_at, like_count, is_repost, web_url, etc.)
- `table`: aligned columns for quick terminal scanning
- `csv`: RFC 4180 CSV with headers for spreadsheets and pipelines

## Exit codes

- `0`: success
- `1`: handle not found, network error, or missing argument

## Agent discovery

```
bskysnap introspect   # JSON: commands, options, types
bskysnap skill        # This SKILL.md
```
