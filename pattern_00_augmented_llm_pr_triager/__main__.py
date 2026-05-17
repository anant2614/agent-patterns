"""CLI: `uv run python -m pattern_00_augmented_llm_pr_triager <PR_URL>`."""

from __future__ import annotations

import asyncio
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent import build_pr_triager
from .tools import parse_pr_url

console = Console()


async def review_pr(pr_reference: str) -> str:
    ref = parse_pr_url(pr_reference)
    agent = build_pr_triager()

    user_message = (
        f"Please review pull request #{ref['pr_number']} in the repository "
        f"{ref['owner']}/{ref['repo']}. Use the tools to fetch its metadata "
        f"and diff before writing your review."
    )

    console.print(
        Panel.fit(
            f"[bold]Reviewing[/bold] {ref['owner']}/{ref['repo']}#{ref['pr_number']}",
            border_style="cyan",
        )
    )

    response = await agent.run(user_message)
    return str(response)


def main() -> int:
    if len(sys.argv) != 2:
        console.print(
            "[red]Usage:[/red] uv run python -m pattern_00_augmented_llm_pr_triager <PR_URL>\n"
            "       e.g. https://github.com/microsoft/agent-framework/pull/1"
        )
        return 2

    try:
        result = asyncio.run(review_pr(sys.argv[1]))
    except ValueError as e:
        console.print(f"[red]Bad input:[/red] {e}")
        return 2
    except Exception as e:  # noqa: BLE001  -- top-level CLI catch
        console.print(f"[red]Error:[/red] {e!r}")
        return 1

    console.print(Markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
