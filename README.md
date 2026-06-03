# Handy

A minimal AI agent built from first principles. Handy can run shell commands, remember what it did, and pick up where it left off — all with a clean, understandable codebase.

---

## What it does

You talk to it. It thinks, runs shell commands, and responds. Every action is saved to disk. Resume any conversation by name.

```
$ uv run python main.py my-session

[conversation: my-session] [0 messages loaded]

> how many python files are in this directory?
[tool call: shell({'command': 'find . -name "*.py" | wc -l'})]
[output: 12]
[exit code: 0]
Assistant: There are 12 Python files in the current directory.

> which one is the largest?
[tool call: shell({'command': 'find . -name "*.py" -exec wc -l {} + | sort -rn | head -1'})]
[output: 247 ./src/runner.py]
[exit code: 0]
Assistant: The largest Python file is src/runner.py with 247 lines.
```

---

## Features

**Persistent event log**
Every user message, tool call, and tool result is written to disk as an individual JSON file — append-only, never mutated. Conversations are fully replayable.

```
conversations/my-session/
  event_0000.json  ← user message
  event_0001.json  ← shell command called
  event_0002.json  ← shell output
  event_0003.json  ← assistant reply
```

**Conversation resume**
Pass a conversation ID to resume exactly where you left off. Each conversation is isolated in its own directory.

```bash
uv run python main.py my-session    # resume or start
uv run python main.py other-session # completely separate conversation
```

**Secret masking**
Register secrets by name. The LLM only sees the name, never the value. Secrets are injected as env vars at execution time. If a secret leaks into tool output, it is masked before hitting the log.

```python
secrets.set("GITHUB_TOKEN", "ghp_abc123")
# LLM writes:  curl -H "Authorization: Bearer $GITHUB_TOKEN" ...
# Log stores:  {"output": "token: <secret-hidden>"}
```

**Context condensation**
When conversation history grows too long, the oldest half is summarized by the LLM into a single paragraph. The condensation is saved as an event — on resume, history is rebuilt from the summary forward, not from scratch.

```
[condenser: 10 messages → summary]
```

**Configurable via `.env`**

```env
LLM_MODEL=gemini/gemini-2.0-flash
LLM_API_KEY=your_key
HISTORY_TURNS=3        # how many events to load on resume (0 = fresh start)
MAX_MESSAGES=20        # trigger condensation after N messages
```

---

## Architecture

```
main.py          — REPL, reads config, wires everything together
src/
  brain.py       — LLM abstraction (litellm), returns typed Response objects
  runner.py      — agent loop: call LLM → execute tools → log events → repeat
  tools.py       — ShellTool: runs commands, supports env var injection
  registry.py    — tool registry: register once, resolve anywhere
  events.py      — event types + EventLog: append to disk, load with condensation awareness
  secrets.py     — SecretRegistry: inject secrets as env vars, mask in outputs
  condenser.py   — summarize old history when context gets too long
```

Each module has one job. Nothing is magic.

---

## Design decisions

**Why event sourcing?**
History is never stored as a single mutable object. Each event is an independent file on disk. You can replay, audit, or resume any conversation without trusting in-memory state.

**Why separate SecretRegistry?**
Secrets should never appear in the event log. By injecting them as env vars at execution time, the command string stays clean — the log only ever sees `$SECRET_NAME`, not the value.

**Why LLM-based condensation?**
When history grows too large for the model context window, you need to compress it. Rule-based truncation loses context. An LLM summary preserves what matters. The condensation event is saved to disk so the compressed view is stable across sessions.

---

## Setup

```bash
git clone https://github.com/MotiBaadror/handy
cd handy
uv sync
```

Copy `.env.example` to `.env` and add your API key:

```env
LLM_MODEL=gemini/gemini-2.0-flash
LLM_API_KEY=your_key_here
```

Run:

```bash
uv run python main.py
```

Requires Python 3.13+. Uses [uv](https://github.com/astral-sh/uv) for dependency management.

Supported models: anything litellm supports — Gemini, OpenAI, Groq, Anthropic, Ollama.

---

## Running tests

```bash
uv run pytest tests/ -v
```

Tests use a `FakeBrain` to verify runner behavior without real LLM calls — error handling, bad tool arguments, unknown tools.