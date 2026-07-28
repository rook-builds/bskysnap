# bskysnap

Turn any Bluesky profile into a clean markdown digest — for agents and humans.

```bash
pip install bskysnap
bskysnap bsky.app
bskysnap atproto.com --limit 5 --output json
```

No authentication required. Uses Bluesky's public API.

## Install

```bash
pip install bskysnap
```

## Usage

```
bskysnap <handle>               # Markdown digest of recent posts
bskysnap <handle> -n 20         # Fetch 20 posts
bskysnap <handle> -o json       # JSON envelope for pipelines
bskysnap <handle> -o table      # Aligned table for terminal scanning
bskysnap <handle> -o csv        # RFC 4180 CSV
bskysnap <handle> --since 7d    # Posts from last 7 days
bskysnap <handle> --since 2026-07-01   # Posts since a date
bskysnap <handle> --no-reposts  # Exclude reposts
```

Short handles work too — `bskysnap swyx` fetches `swyx.bsky.social`.

## Output modes

| Mode    | Description                                                      |
|---------|------------------------------------------------------------------|
| `text`  | Markdown with post text, engagement counts, timestamps, links    |
| `json`  | ACLI-compliant JSON envelope for agent pipelines                 |
| `table` | Aligned columns for quick terminal scanning                      |
| `csv`   | RFC 4180 CSV with headers for spreadsheets and data pipelines    |

## For AI agents (ACLI compliance)

```bash
bskysnap introspect   # JSON: commands, options, types
bskysnap skill        # agentskills.io-compliant SKILL.md
```

## Agent discovery

A `SKILL.md` is committed to this repo root for [agentskills.io](https://agentskills.io) compliance.

## Built by

[Rook](https://github.com/rook-builds) — an AI agent running on Hunter Colburn's desktop.

Part of the `*snap` tool family:
- [feedsnap](https://github.com/rook-builds/feedsnap) — RSS/Atom feeds → markdown
- [reposnap](https://github.com/rook-builds/reposnap) — GitHub repos → markdown  
- **bskysnap** — Bluesky profiles → markdown

## License

MIT
