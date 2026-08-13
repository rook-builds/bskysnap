# Changelog

## [0.2.0] - 2026-08-12

### Added
- `bskysnap serve [--port 8080] [--host localhost]` — stateless MCP HTTP server
- Implements MCP 2026-07-28 specification (single POST /mcp per request, no session state)
- `tools/list` endpoint returns JSON Schema for the `fetch` tool (handle required; limit, since, no_reposts optional)
- `tools/call fetch` accepts handle, limit, since, no_reposts and returns a markdown digest
- `GET /mcp` health check returns name, version, spec version
- `handle_mcp_request()` pure function — fully unit-testable without a real HTTP server
- 13 new unit tests in `tests/test_mcp_server.py`
- Zero new runtime dependencies (stdlib only)
- `--port / -p` and `--host` CLI options added

## [0.1.0] - 2026-07-28

### Added
- `bskysnap <handle>` — fetch posts from any public Bluesky profile
- `--output [text|json|table|csv]` — four output modes
  - `text`: markdown with post text, engagement counts, timestamps, links
  - `json`: ACLI-compliant JSON envelope for agent pipelines  
  - `table`: aligned columns for terminal scanning
  - `csv`: RFC 4180 CSV for spreadsheets and data pipelines
- `--limit N` / `-n N` — control number of posts (default 10)
- `--since DATE` — filter posts by date (YYYY-MM-DD or Nd, e.g. `7d`)
- `--no-reposts` — exclude reposts from output
- `bskysnap introspect` — ACLI-compliant JSON description of commands and options
- `bskysnap skill` — agentskills.io-compliant SKILL.md
- `SKILL.md` at repo root for agent discovery
- Short handle support: `bskysnap swyx` → fetches `swyx.bsky.social`
- No authentication required — uses Bluesky's public API only
- 59 tests across 4 test files
