# agent-patterns

Runnable demos of every pattern from Anthropic's
[**Building Effective Agents**](https://www.anthropic.com/engineering/building-effective-agents),
implemented with the [Microsoft Agent Framework (Python)](https://learn.microsoft.com/en-us/agent-framework/).

Each folder is a self-contained demo that maps one Anthropic pattern to a MAF primitive,
plus a `README.md` explaining the concept, the architecture, and how to run it.

| # | Anthropic pattern | MAF primitive | Demo | Status |
|---|---|---|---|---|
| 0 | Augmented LLM | `Agent` + function tools | **GitHub PR Triager** — fetch diff, summarise, risk-score | ✅ scaffolded |
| 1 | Prompt Chaining | `WorkflowBuilder` sequential edges | Release-notes generator | 🔜 |
| 2 | Routing | `WorkflowBuilder` conditional edges | Cost-aware model router | 🔜 |
| 3 | Parallelization | `ConcurrentBuilder` + aggregator | Code security reviewer (voting) + Resume↔JD scorer (sectioning) | 🔜 |
| 4 | Orchestrator-Workers | `MagenticBuilder` | Deep-research report builder | 🔜 |
| 5 | Evaluator-Optimizer | `WorkflowBuilder` loop with conditional edge | Cold-outreach email writer | 🔜 |
| 6 | Autonomous Agent | `Agent` with tool loop | GitHub issue → PR resolver | 🔜 |

## Quick start

Requirements:
- Python 3.12 (`uv python pin 3.12` already done; uv will install if missing)
- [uv](https://docs.astral.sh/uv/) for env management
- Azure OpenAI resource with a chat-model deployment (e.g. `gpt-4o-mini`)
- `az login` once (we use `AzureCliCredential` by default — no keys in code)

```powershell
# 1. Install deps
uv sync

# 2. Configure environment
copy .env.example .env
# then edit .env with your AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, GITHUB_TOKEN

# 3. Sign into Azure for AAD-based auth
az login

# 4. Run Pattern 0
uv run python -m pattern_00_augmented_llm_pr_triager https://github.com/anant2614/agent-patterns/pull/1
```

## Why MAF?

Because each Anthropic pattern has a near 1:1 primitive in MAF — see the table above.
That means each demo is small enough to read in one sitting, and the *shape* of the code
mirrors the *shape* of the pattern. No framework-induced abstraction tax.

## Repo layout

```
agent-patterns/
├── shared/                            # Reusable helpers (chat client, env loading)
├── pattern_00_augmented_llm_pr_triager/
│   ├── README.md                      # Concept, architecture, run instructions
│   ├── __main__.py                    # CLI entry: `python -m pattern_00_...`
│   ├── agent.py                       # Agent factory
│   └── tools.py                       # GitHub API tools
├── pyproject.toml
├── .env.example
└── .python-version
```

## Learning path

This repo is part of a longer learning journey culminating in multi-agent handoff
with sandbox forking (per [Ivan Burazin's tweet](https://x.com/ivanburazin/status/2055362675845013646)).
See [the plan](#) for the full trajectory.

## License

MIT — see [LICENSE](LICENSE).
