from .brain import Brain
from .events import CondensationEvent, EventLog


class Condenser:
    def __init__(self, brain: Brain, log: EventLog, max_messages: int = 20, keep_first: int = 1):
        self.brain = brain
        self.log = log
        self.max_messages = max_messages
        self.keep_first = keep_first  # how many leading messages to never summarize

    def maybe_condense(self, history: list[dict]) -> list[dict]:
        if len(history) <= self.max_messages:
            return history

        protected = history[:self.keep_first]
        condensable = history[self.keep_first:]

        keep = self.max_messages // 2
        cut = len(condensable) - keep

        # snap cut back to nearest user message so we never split an action+observation pair
        while cut > 0 and condensable[cut].get("role") != "user":
            cut -= 1

        to_summarize = condensable[:cut]
        to_keep = condensable[cut:]

        summary = self._summarize(to_summarize)
        self.log.append(CondensationEvent(summary=summary, forgotten_count=len(to_summarize), summary_offset=self.keep_first))
        print(f"[condenser: {len(to_summarize)} messages → summary]")

        return protected + [{"role": "user", "content": f"[Summary of earlier conversation]: {summary}"}] + to_keep

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