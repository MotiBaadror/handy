from .brain import Brain
from .events import CondensationEvent, EventLog


class Condenser:
    def __init__(self, brain: Brain, log: EventLog, max_messages: int = 20):
        self.brain = brain
        self.log = log
        self.max_messages = max_messages

    def maybe_condense(self, history: list[dict]) -> list[dict]:
        if len(history) <= self.max_messages:
            return history

        keep = self.max_messages // 2
        to_summarize = history[:-keep]
        to_keep = history[-keep:]

        summary = self._summarize(to_summarize)
        self.log.append(CondensationEvent(summary=summary, forgotten_count=len(to_summarize)))
        print(f"[condenser: {len(to_summarize)} messages → summary]")

        return [{"role": "user", "content": f"[Summary of earlier conversation]: {summary}"}] + to_keep

    def _summarize(self, messages: list[dict]) -> str:
        formatted = _format(messages)
        prompt = [{"role": "user", "content": f"Summarize this conversation history in 2-3 sentences:\n\n{formatted}"}]
        response = self.brain.call(prompt)
        return response.content or "Earlier conversation omitted."


def _format(messages: list[dict]) -> str:
    lines = []
    for m in messages:
        role = m.get("role", "unknown")
        if "tool_calls" in m:
            for tc in m["tool_calls"]:
                name = tc["function"]["name"]
                args = tc["function"]["arguments"]
                lines.append(f"Assistant called: {name}({args})")
        elif role == "tool":
            lines.append(f"Tool result: {m.get('content', '')}")
        else:
            lines.append(f"{role.capitalize()}: {m.get('content', '')}")
    return "\n".join(lines)