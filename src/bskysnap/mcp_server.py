"""bskysnap MCP server — stateless MCP 2026-07-28 spec.

Start with:  bskysnap serve [--port 8080] [--host localhost]

The endpoint is a single ``POST /mcp`` that accepts a JSON-RPC 2.0 request
and returns a JSON-RPC 2.0 response.  No sessions, no state.

Methods supported
-----------------
``tools/list``
    Returns the schema for the ``fetch`` tool.
``tools/call`` (name=fetch)
    Calls ``get_author_feed()`` and returns a markdown digest.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from .fetcher import get_author_feed
from .formatter import to_text

# --------------------------------------------------------------------------- #
# Tool schema
# --------------------------------------------------------------------------- #

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "fetch",
        "description": (
            "Fetch recent posts from any Bluesky profile. "
            "Returns a markdown digest of the profile and posts."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["handle"],
            "properties": {
                "handle": {
                    "type": "string",
                    "description": (
                        "Bluesky handle, e.g. 'bsky.app' or 'swyx'. "
                        "Short handles without a dot get .bsky.social appended automatically."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of posts to return (1-100). Defaults to 10.",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
                "since": {
                    "type": "string",
                    "description": (
                        "Only return posts since this date. "
                        "YYYY-MM-DD or Nd (e.g. '7d' for the last 7 days)."
                    ),
                },
                "no_reposts": {
                    "type": "boolean",
                    "description": "If true, exclude reposts. Defaults to false.",
                    "default": False,
                },
            },
        },
    }
]

# --------------------------------------------------------------------------- #
# Pure request handler (no HTTP, fully testable)
# --------------------------------------------------------------------------- #


def handle_mcp_request(body: dict[str, Any]) -> dict[str, Any]:
    """Handle a stateless MCP JSON-RPC 2.0 request dict; return response dict.

    This is the heart of the server and is deliberately free of any HTTP
    concerns so it can be unit-tested without spinning up a real server.
    """
    req_id = body.get("id", 1)
    method = body.get("method", "")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": _TOOLS},
        }

    if method == "tools/call":
        params = body.get("params", {})
        name = params.get("name", "")
        args = params.get("arguments", {})

        if name != "fetch":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {name!r}.  Available tools: fetch",
                },
            }

        handle = args.get("handle", "")
        limit = int(args.get("limit", 10))
        since = args.get("since", None)
        no_reposts = bool(args.get("no_reposts", False))

        profile, posts = get_author_feed(
            handle,
            limit=limit,
            include_reposts=not no_reposts,
            since=since,
        )
        text = to_text(profile, posts)

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": text}],
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Unknown method: {method!r}.  Supported: tools/list, tools/call",
        },
    }


# --------------------------------------------------------------------------- #
# HTTP handler
# --------------------------------------------------------------------------- #


class _MCPHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler for the stateless MCP endpoint."""

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/mcp":
            self._send(404, {"error": "not found"})
            return
        from . import __version__

        self._send(
            200,
            {
                "name": "bskysnap",
                "version": __version__,
                "spec": "2026-07-28",
                "endpoint": "POST /mcp",
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/mcp":
            self._send(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            raw = self.rfile.read(length)
            body: dict[str, Any] = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            self._send(
                400,
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error: invalid JSON"},
                },
            )
            return

        response = handle_mcp_request(body)
        self._send(200, response)

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: N802
        # Suppress default per-request logging.
        pass


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #


def serve(host: str = "localhost", port: int = 8080) -> None:
    """Start the blocking MCP HTTP server.

    Press Ctrl-C to stop.
    """
    server = HTTPServer((host, port), _MCPHandler)
    print(f"bskysnap MCP server → http://{host}:{port}/mcp")
    print("  POST /mcp   tools/list | tools/call")
    print("  GET  /mcp   health check")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
