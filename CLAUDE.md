# Handy — Project Rules

## What this project is

`handy` is an original personal agent project. It is NOT a clone or copy of any existing
framework. The design decisions, naming, structure, and use case are all independently
conceived.

The learning inspiration comes from studying how agent systems work internally, but
nothing is borrowed — every line is written from first principles with original naming
and original design.

**This is a portfolio project. It must stand on its own.**

## Identity rules

- **Own naming.** Do not use names from other frameworks. Pick names that reflect how
  YOU think about the system.
- **Own structure.** File layout and architecture should follow what makes sense for
  this project, not mirror anything else.
- **Own use case.** Built around a real problem worth solving, with a clear story:
  "I built this to do X" — not "I reimplemented Y."
- **Own README.** Explains the problem, the design choices, and why it exists.

## How we build

- **Every line must be understood.** No copy-pasting, no blind borrowing.
- **One concept at a time.** Only implement what is fully understood.
- **One commit per concept.** Each commit is a single, coherent idea.
- **Commit messages explain WHY.** Not "add run loop" but "add run loop: without this
  the agent calls the LLM once and stops — it needs to keep looping until the LLM
  signals it is done."
- **Failures drive additions.** Before adding code, understand what breaks without it.
  The commit message should describe that failure.

## Learning and building process

Before implementing anything new, follow this exact sequence:

1. **Understand first** — read how the SDK does it, explain it clearly before touching code
2. **Plan explicitly** — list every file that changes and why, wait for confirmation
3. **Learn from the SDK's design** — ask "why did they build it this way?" before copying the pattern
4. **Build the naive version first** — implement the simplest thing, run it, break it
5. **Identify what breaks** — observe the failure, understand the root cause
6. **Fix with understanding** — add only what's needed to fix the specific failure
7. **Commit** — one concept, explain why in the message

**Never skip step 1-3.** Jumping straight to code means missing important design
decisions (like `is_error`, exit code context, image support) that only become
obvious when you understand the full picture first.

## Commit message format

```
<what>: <why it's needed / what breaks without it>

Example:
"add corrective nudge: without this, reasoning-only responses silently stall the loop
 because the model gets no signal that it needs to produce an action or a reply"
```

## Backlog (known gaps, not implemented yet)

1. **Sandbox the shell tool** — currently runs commands directly on local machine, no restrictions
2. **Handle model_validate failure** — what happens when the LLM returns bad tool arguments and Pydantic rejects them
3. ~~**Action type hardcoded in Runner**~~ — fixed, tools now injected and own their action via `build_action()`
4. **Tool result format** — currently plain string; SDK supports `TextContent | ImageContent` for richer output (e.g. screenshots)
5. **History explosion** — conversation history grows forever, no condensation or truncation yet

## Learning notes

Full learning notes live in the openhands-sdk repo at
`data/learning_repo_and_trying.md`. Use those as reference for understanding,
not as a blueprint to copy.