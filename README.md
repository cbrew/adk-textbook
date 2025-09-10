# ADK Research Textbook — Project Setup (Python 3.13+, uv)

This repo hosts a multi-chapter, demo-driven “small textbook” for Google’s Agent Development Kit (ADK) in the **academic research** domain.  

The running theme is supposed to be evaluation. Evaluation is very new in ADK, with the main sources being blog posts by
Google Developer Advocates Megan O'Keefe and Raphael



Chapter 1 lives in `textbook-adk-ch01/` and runs **without writing Python code** (config-only), but we’ll set up a proper project environment 
right away.

> Requires: **Python 3.13+** and **uv** (fast Python package manager).  
> Install uv (macOS/Linux): `curl -LsSf https://astral.sh/uv/install.sh | sh`  
> Windows (PowerShell): `irm https://astral.sh/uv/install.ps1 | iex`

---

## 1) Initialize the project with uv

From the **project root** (the parent of `textbook-adk-ch01/`):

```bash
uv init
```

This creates a `pyproject.toml`. Now pin the Python requirement to 3.13+ by editing the generated file:

```toml
[project]
name = "adk-textbook"
version = "0.1.0"
description = "Short, demo-first textbook for Google ADK (academic research domain)"
readme = "README.md"
requires-python = ">=3.13"
```

(uv respects `requires-python`. You don’t need to activate a venv manually to use `uv run`, but you can create one if you like.)

## 2) Add dependencies (with eval extras)

Install ADK (with evaluation extras), LiteLLM, and dotenv:

```bash
uv add "google-adk[eval]" litellm python-dotenv
```

If you prefer to track the very latest main branch instead of a release:

```bash
uv add "google-adk[eval] @ git+https://github.com/google/adk-python.git@main"
```

---

## 3) Configure model API keys

Create a `.env` file at the **project root** (not committed by default; add to `.gitignore` if needed):

```dotenv
# Pick whichever providers you plan to use (LiteLLM can route to many):
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...            # for Gemini (if used)
GOOGLE_CSE_ID=...             # if using a Google Custom Search tool
SERPAPI_API_KEY=...           # if you plug in SerpAPI-based search
```

---

## 4) Verify the toolchain

```bash
uv run adk --help
uv run python -c "import litellm; print('LiteLLM ok')"
```

---

## 5) Run Chapter 1 (config-only agent)

From the **project root**:

```bash
uv run adk run textbook-adk-ch01/config/basic_research_agent.yaml
```

Or launch the web UI:

```bash
uv run adk web textbook-adk-ch01/config/basic_research_agent.yaml
```

Replay saved tests:

```bash
uv run adk eval textbook-adk-ch01/tests/
```

---

## 6) Common tasks (optional Makefile)

```make
.PHONY: run web eval
run:
	uv run adk run textbook-adk-ch01/config/basic_research_agent.yaml

web:
	uv run adk web textbook-adk-ch01/config/basic_research_agent.yaml

eval:
	uv run adk eval textbook-adk-ch01/tests/
```

---

## 7) Troubleshooting

- **`adk: command not found`**  
  Ensure the package is installed in this project (`uv add "google-adk[eval]"`) and invoke via `uv run adk ...`.
- **Model auth errors**  
  Double-check `.env` is populated and that your chosen provider is enabled in LiteLLM / ADK config.
- **Search tools**  
  Some search tools require separate API keys (e.g., SerpAPI, Google Custom Search).

---

## 8) What's next?

### Chapter Structure

This textbook follows a progressive learning approach:

| Chapter | Focus | Technology Stack |
|---------|-------|------------------|
| **[Chapter 1](textbook-adk-ch01/)** | Config-only agents | YAML configuration files |
| **[Chapter 2](textbook-adk-ch02/)** | Python-based agents | Custom tools, evaluation frameworks |
| **[Chapter 6](textbook-adk-ch06-runtime/)** | ADK Runtime Fundamentals | FastAPI, state management, UI contracts |
| **[Chapter 7](textbook-adk-ch07-runtime/)** | PostgreSQL Runtime | Database persistence, custom services |

### Getting Started

- **New to ADK?** Start with `textbook-adk-ch01/README.md` for the no-code walkthrough
- **Ready for Python?** Move to `textbook-adk-ch02/README.md` for custom tools and agents  
- **Want to understand runtimes?** Explore `textbook-adk-ch06-runtime/README.md` for ADK internals
- **Building production systems?** See `textbook-adk-ch07-runtime/README.md` for PostgreSQL integration
