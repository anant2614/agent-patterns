"""Function tools for the PR Triager.

Notes for future-you on tool design (from Anthropic's "Agent-Computer Interface"
guidance):

- Every tool has a docstring; the model reads it.
- Parameter names are unambiguous (`owner`, `repo`, `pr_number` — not `o`, `r`, `n`).
- Return shapes are stable dicts with documented keys.
- Big payloads (diffs) are *truncated structurally*, not arbitrarily, so the model
  never has to count tokens or recover from a half-truncated patch hunk.
"""

from __future__ import annotations

import os
import re
from typing import TypedDict

import httpx

GITHUB_API = "https://api.github.com"
MAX_DIFF_BYTES = 60_000  # ~15k tokens; safe for any modern chat model
USER_AGENT = "agent-patterns/pr-triager"


class PullRequestRef(TypedDict):
    owner: str
    repo: str
    pr_number: int


_URL_PATTERNS = [
    # https://github.com/owner/repo/pull/123  (with optional trailing /files etc.)
    re.compile(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<pr_number>\d+)"),
    # owner/repo#123  shorthand
    re.compile(r"^(?P<owner>[^/]+)/(?P<repo>[^/#]+)#(?P<pr_number>\d+)$"),
]


def parse_pr_url(value: str) -> PullRequestRef:
    """Parse a PR URL or `owner/repo#N` shorthand into its parts.

    Raises:
        ValueError: if the input doesn't look like a PR reference.
    """
    value = value.strip()
    for pattern in _URL_PATTERNS:
        match = pattern.search(value)
        if match:
            return {
                "owner": match["owner"],
                "repo": match["repo"],
                "pr_number": int(match["pr_number"]),
            }
    raise ValueError(
        f"Could not parse PR reference {value!r}. "
        f"Expected something like https://github.com/owner/repo/pull/123 "
        f"or owner/repo#123."
    )


def _headers(accept: str = "application/vnd.github+json") -> dict[str, str]:
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_pr_metadata(owner: str, repo: str, pr_number: int) -> dict:
    """Fetch high-level metadata for a GitHub pull request.

    Args:
        owner: GitHub owner / org, e.g. "microsoft".
        repo: Repository name, e.g. "agent-framework".
        pr_number: The pull request number.

    Returns:
        A dict with keys:
            title, author, state, draft, body,
            base_branch, head_branch,
            additions, deletions, changed_files,
            files: list of {filename, status, additions, deletions} (up to 100),
            url.
    """
    with httpx.Client(timeout=20.0) as client:
        pr_resp = client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=_headers(),
        )
        pr_resp.raise_for_status()
        pr = pr_resp.json()

        files_resp = client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=_headers(),
            params={"per_page": 100},
        )
        files_resp.raise_for_status()
        files = files_resp.json()

    return {
        "title": pr.get("title"),
        "author": (pr.get("user") or {}).get("login"),
        "state": pr.get("state"),
        "draft": pr.get("draft", False),
        "body": (pr.get("body") or "")[:4000],
        "base_branch": (pr.get("base") or {}).get("ref"),
        "head_branch": (pr.get("head") or {}).get("ref"),
        "additions": pr.get("additions"),
        "deletions": pr.get("deletions"),
        "changed_files": pr.get("changed_files"),
        "files": [
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "additions": f.get("additions"),
                "deletions": f.get("deletions"),
            }
            for f in files
        ],
        "url": pr.get("html_url"),
    }


def fetch_pr_diff(owner: str, repo: str, pr_number: int) -> dict:
    """Fetch the unified diff for a pull request.

    If the diff is larger than MAX_DIFF_BYTES, it is truncated at a file
    boundary and a `truncated` flag is set so the model knows it isn't seeing
    the whole picture.

    Returns:
        {
            "diff": str,
            "truncated": bool,
            "total_bytes": int,
            "shown_bytes": int,
            "shown_files": int,
        }
    """
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}",
            headers=_headers(accept="application/vnd.github.v3.diff"),
        )
        resp.raise_for_status()
        full_diff = resp.text

    total_bytes = len(full_diff.encode("utf-8"))
    if total_bytes <= MAX_DIFF_BYTES:
        return {
            "diff": full_diff,
            "truncated": False,
            "total_bytes": total_bytes,
            "shown_bytes": total_bytes,
            "shown_files": full_diff.count("\ndiff --git ") + (1 if full_diff.startswith("diff --git ") else 0),
        }

    # Truncate at a file boundary so the model gets whole hunks.
    file_chunks = re.split(r"(?m)^(?=diff --git )", full_diff)
    kept: list[str] = []
    running = 0
    for chunk in file_chunks:
        chunk_bytes = len(chunk.encode("utf-8"))
        if running + chunk_bytes > MAX_DIFF_BYTES and kept:
            break
        kept.append(chunk)
        running += chunk_bytes

    truncated = "".join(kept)
    return {
        "diff": truncated,
        "truncated": True,
        "total_bytes": total_bytes,
        "shown_bytes": len(truncated.encode("utf-8")),
        "shown_files": max(1, len(kept) - (1 if kept and kept[0] == "" else 0)),
    }
