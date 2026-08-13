"""Tests for bskysnap MCP server.

All tests operate on the pure ``handle_mcp_request()`` function — no real
HTTP server, no real Bluesky API calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from bskysnap.mcp_server import _TOOLS, handle_mcp_request

# --------------------------------------------------------------------------- #
# Shared mock data
# --------------------------------------------------------------------------- #

_FAKE_PROFILE = MagicMock()
_FAKE_PROFILE.handle = "bsky.app"
_FAKE_PROFILE.display_name = "Bluesky"
_FAKE_POSTS = [MagicMock()]
_FAKE_TEXT = "# Bluesky: @bsky.app\n\nSome posts here."


def _list_body(req_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "method": "tools/list"}


def _call_body(arguments: dict, req_id: int = 1) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": "fetch", "arguments": arguments},
    }


# --------------------------------------------------------------------------- #
# tools/list
# --------------------------------------------------------------------------- #


def test_tools_list_contains_fetch_tool():
    resp = handle_mcp_request(_list_body())
    names = [t["name"] for t in resp["result"]["tools"]]
    assert "fetch" in names


def test_tools_list_handle_property_present():
    resp = handle_mcp_request(_list_body())
    fetch = next(t for t in resp["result"]["tools"] if t["name"] == "fetch")
    assert "handle" in fetch["inputSchema"]["properties"]


def test_tools_list_handle_is_required():
    resp = handle_mcp_request(_list_body())
    fetch = next(t for t in resp["result"]["tools"] if t["name"] == "fetch")
    assert "handle" in fetch["inputSchema"]["required"]


def test_tools_list_preserves_request_id():
    resp = handle_mcp_request(_list_body(req_id=42))
    assert resp["id"] == 42


# --------------------------------------------------------------------------- #
# tools/call — happy paths
# --------------------------------------------------------------------------- #


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_returns_text_content(mock_feed, mock_text):
    resp = handle_mcp_request(_call_body({"handle": "bsky.app"}))
    content = resp["result"]["content"]
    assert content[0]["type"] == "text"
    assert content[0]["text"] == _FAKE_TEXT


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_default_limit_is_10(mock_feed, mock_text):
    handle_mcp_request(_call_body({"handle": "bsky.app"}))
    assert mock_feed.call_args[1]["limit"] == 10


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_custom_limit(mock_feed, mock_text):
    handle_mcp_request(_call_body({"handle": "bsky.app", "limit": 25}))
    assert mock_feed.call_args[1]["limit"] == 25


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_since_passed_through(mock_feed, mock_text):
    handle_mcp_request(_call_body({"handle": "bsky.app", "since": "7d"}))
    assert mock_feed.call_args[1]["since"] == "7d"


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_since_defaults_to_none(mock_feed, mock_text):
    handle_mcp_request(_call_body({"handle": "bsky.app"}))
    assert mock_feed.call_args[1]["since"] is None


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_no_reposts_true_sets_include_reposts_false(mock_feed, mock_text):
    handle_mcp_request(_call_body({"handle": "bsky.app", "no_reposts": True}))
    assert mock_feed.call_args[1]["include_reposts"] is False


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_no_reposts_false_sets_include_reposts_true(mock_feed, mock_text):
    handle_mcp_request(_call_body({"handle": "bsky.app", "no_reposts": False}))
    assert mock_feed.call_args[1]["include_reposts"] is True


@patch("bskysnap.mcp_server.to_text", return_value=_FAKE_TEXT)
@patch("bskysnap.mcp_server.get_author_feed", return_value=(_FAKE_PROFILE, _FAKE_POSTS))
def test_tools_call_preserves_request_id(mock_feed, mock_text):
    resp = handle_mcp_request(_call_body({"handle": "bsky.app"}, req_id=99))
    assert resp["id"] == 99


# --------------------------------------------------------------------------- #
# tools/call — error paths
# --------------------------------------------------------------------------- #


def test_tools_call_unknown_tool_returns_error():
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "nonexistent", "arguments": {}},
    }
    resp = handle_mcp_request(body)
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_unknown_method_returns_error():
    resp = handle_mcp_request({"jsonrpc": "2.0", "id": 1, "method": "ping"})
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_unknown_method_preserves_id():
    resp = handle_mcp_request({"jsonrpc": "2.0", "id": 7, "method": "ping"})
    assert resp["id"] == 7
