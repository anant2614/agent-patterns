"""Pattern 0 — Augmented LLM: GitHub PR Triager.

A single ChatAgent enhanced with two function tools (`fetch_pr_metadata`,
`fetch_pr_diff`) that reviews any GitHub pull request and emits a summary,
risk score, and suggested reviewer focus areas.

This is the "augmented LLM" building block from Anthropic's article — the
foundation every other pattern composes.
"""

from .agent import build_pr_triager
from .tools import fetch_pr_metadata, fetch_pr_diff, parse_pr_url

__all__ = ["build_pr_triager", "fetch_pr_metadata", "fetch_pr_diff", "parse_pr_url"]
