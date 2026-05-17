# Pattern 0 — Augmented LLM: GitHub PR Triager

> **Anthropic pattern:** [Augmented LLM](https://www.anthropic.com/engineering/building-effective-agents#building-block-the-augmented-llm)
> — an LLM enhanced with tools, retrieval, and memory. The foundational building
> block that every other pattern composes.
>
> **MAF primitive:** [`Agent`](https://learn.microsoft.com/en-us/agent-framework/agents/) (chat-client-backed) with function tools.

## What this demo does

You give it a GitHub PR URL. It:

1. Calls `fetch_pr_metadata` (tool) to get title, author, body, files-changed counts.
2. Calls `fetch_pr_diff` (tool) to read the unified diff.
3. Returns a structured review:
   - **Summary** (2–3 sentences of what the PR does)
   - **Risk Score** — `low` / `medium` / `high`
   - **Risk Factors** — bullet list of concrete concerns (security, correctness, perf, tests)
   - **Suggested Focus Areas** for human reviewers
   - **Hot Files** — files most worth eyeballing first

## Architecture

```
┌──────────────────────────┐
│         CLI input        │   github.com/owner/repo/pull/123
│   (PR URL or shorthand)  │
└─────────────┬────────────┘
              ▼
       ┌─────────────┐         ┌──────────────────────┐
       │    Agent    │ ──────► │ fetch_pr_metadata()  │ ──► GitHub REST
       │   (Azure    │         └──────────────────────┘
       │   OpenAI)   │         ┌──────────────────────┐
       │             │ ──────► │ fetch_pr_diff()      │ ──► GitHub REST
       │  instructions:        │ (truncated if huge)  │
       │  "senior code         └──────────────────────┘
       │   reviewer"  │
       └──────┬──────┘
              ▼
        Markdown review
       (printed via Rich)
```

The "augmented LLM" pattern is the agent loop in its simplest form:

> *LLM → choose tool → call tool → observe → repeat → emit answer.*

MAF handles the loop for you when you pass tools to `Agent`.

## Run it

```powershell
# From repo root, after `uv sync` and configuring .env:
uv run python -m pattern_00_augmented_llm_pr_triager <PR_URL>

# Examples (any of these formats):
uv run python -m pattern_00_augmented_llm_pr_triager https://github.com/microsoft/agent-framework/pull/1
uv run python -m pattern_00_augmented_llm_pr_triager github.com/anthropics/anthropic-quickstarts/pull/40
uv run python -m pattern_00_augmented_llm_pr_triager microsoft/agent-framework#1
```

## Concepts demonstrated

| Concept | Where to look |
|---|---|
| Defining function tools | `tools.py` — note the rich type hints and docstrings (this is the *Agent-Computer Interface* the article emphasises) |
| Wiring tools into an agent | `agent.py:build_pr_triager` |
| Instruction prompt | `agent.py:INSTRUCTION` |
| Calling the agent | `__main__.py` |
| Sensible truncation of big diffs | `tools.py:fetch_pr_diff` — diffs over `MAX_DIFF_BYTES` get summarised structurally |

## What surprised me

> *(Fill this in after running a few PRs through it — what worked, what didn't,
> what you'd change if you wrote it again.)*
