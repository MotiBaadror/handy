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
3. **Action type hardcoded in Runner** — `ShellAction(**args)` assumes only one tool; each tool should build its own action from args

## Learning notes

Full learning notes live in the openhands-sdk repo at
`data/learning_repo_and_trying.md`. Use those as reference for understanding,
not as a blueprint to copy.