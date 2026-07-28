"""ACLI introspection and agentskills.io SKILL.md for bskysnap."""

# NOTE: Do NOT import __version__ from __init__.py here.
# __init__.py imports from introspect.py, so importing back
# would cause a partially-initialized module error (circular import).
# Hardcode the version instead; bump this alongside pyproject.toml and __init__.py.
_TOOL_VERSION = "0.1.0"


def get_introspect_json() -> str:
    """Return ACLI-compliant JSON description of bskysnap."""
    import json

    data = {
        "tool": "bskysnap",
        "version": _TOOL_VERSION,
        "description": (
            "Turn any public Bluesky profile into a clean markdown digest. "
            "No authentication required."
        ),
        "commands": {
            "default": {
                "description": "Fetch posts from a Bluesky handle.",
                "arguments": [
                    {
                        "name": "handle",
                        "type": "string",
                        "required": False,
                        "description": "Bluesky handle (e.g. bsky.app or swyx). Short handles get .bsky.social appended.",
                    }
                ],
                "options": {
                    "--limit": {
                        "short": "-n",
                        "type": "integer",
                        "default": 10,
                        "description": "Number of posts to return.",
                    },
                    "--output": {
                        "short": "-o",
                        "type": "string",
                        "choices": ["text", "json", "table", "csv"],
                        "default": "text",
                        "description": "Output format.",
                    },
                    "--no-reposts": {
                        "type": "boolean",
                        "default": False,
                        "description": "Exclude reposts from output.",
                    },
                    "--since": {
                        "type": "string",
                        "default": None,
                        "description": "Show posts since date: YYYY-MM-DD or Nd (e.g. 7d).",
                    },
                },
            },
            "introspect": {
                "description": "Print ACLI-compliant JSON description of this tool.",
            },
            "skill": {
                "description": "Print agentskills.io-compliant SKILL.md.",
            },
        },
    }
    return json.dumps(data, indent=2)


def get_skill_md() -> str:
    """Return agentskills.io-compliant SKILL.md content."""
    return f"""\
---
name: bskysnap
description: Fetch posts from any public Bluesky profile and format them as markdown, JSON, table, or CSV. Use when you need to monitor a Bluesky account, summarize recent posts, or pipe social content into an agent workflow. No authentication required.
license: MIT
metadata:
  author: rook-builds
  version: {_TOOL_VERSION}
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
- `json`: ACLI envelope with structured post objects (uri, text, created\\_at, like\\_count, is\\_repost, web\\_url, etc.)
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
"""
