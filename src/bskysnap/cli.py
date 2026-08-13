"""bskysnap CLI — turn any Bluesky profile into a clean markdown digest."""

import sys

import click

from .fetcher import get_author_feed
from .formatter import to_csv, to_json, to_table, to_text
from .introspect import get_introspect_json, get_skill_md

_ACLI_COMMANDS = {"introspect", "skill", "serve"}


def _handle_acli_command(cmd: str, host: str, port: int) -> None:
    if cmd == "introspect":
        print(get_introspect_json())
    elif cmd == "skill":
        print(get_skill_md())
    elif cmd == "serve":
        from .mcp_server import serve as run_serve

        run_serve(host=host, port=port)


@click.command()
@click.argument("handle", required=False, default=None)
@click.option("--limit", "-n", default=10, show_default=True, help="Number of posts to fetch.")
@click.option(
    "--output",
    "-o",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json", "table", "csv"]),
    help="Output format.",
)
@click.option("--no-reposts", is_flag=True, default=False, help="Exclude reposts from output.")
@click.option(
    "--since",
    default=None,
    help="Show posts since date: YYYY-MM-DD or Nd (e.g. 7d).",
)
@click.option("--port", "-p", default=8080, show_default=True, help="Port for MCP server (serve mode).")
@click.option("--host", default="localhost", show_default=True, help="Host for MCP server (serve mode).")
def main(handle, limit, output, no_reposts, since, port, host):
    """Turn any Bluesky profile into a clean markdown digest.

    HANDLE is a Bluesky handle (e.g. bsky.app or swyx). Short handles without
    a dot get .bsky.social appended automatically.

    \b
    Special commands: bskysnap introspect | bskysnap skill
    MCP server:       bskysnap serve [--port 8080] [--host localhost]
    """
    # ACLI command dispatch (must come before handle validation)
    if handle in _ACLI_COMMANDS:
        _handle_acli_command(handle, host=host, port=port)
        sys.exit(0)

    if handle is None:
        click.echo("Error: Missing argument 'HANDLE'. Try: bskysnap bsky.app", err=True)
        sys.exit(1)

    profile, posts = get_author_feed(
        handle,
        limit=limit,
        include_reposts=not no_reposts,
        since=since,
    )

    if output == "text":
        click.echo(to_text(profile, posts))
    elif output == "json":
        click.echo(to_json(profile, posts))
    elif output == "table":
        click.echo(to_table(posts))
    elif output == "csv":
        click.echo(to_csv(posts), nl=False)
