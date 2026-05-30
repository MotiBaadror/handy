import json
from pathlib import Path

from .brain import Brain
from .events import ActionEvent, Event, EventLog, MessageEvent, ObservationEvent

NUDGE = (
    "Your last response was empty. "
    "Please reply with something useful."
)


def _rebuild_history(events: list[Event]) -> list[dict]:
    history = []
    i = 0
    while i < len(events):
        event = events[i]
        if isinstance(event, MessageEvent):
            history.append({"role": event.role, "content": event.content})
            i += 1
        elif isinstance(event, ActionEvent):
            # consecutive ActionEvents belong to the same LLM response
            tool_calls = []
            while i < len(events) and isinstance(events[i], ActionEvent):
                ae = events[i]
                tool_calls.append({
                    "id": ae.tool_call_id,
                    "type": "function",
                    "function": {"name": ae.tool_name, "arguments": json.dumps(ae.args)},
                })
                i += 1
            history.append({"role": "assistant", "tool_calls": tool_calls})
        elif isinstance(event, ObservationEvent):
            history.append({
                "role": "tool",
                "tool_call_id": event.tool_call_id,
                "content": event.output,
            })
            i += 1
    return history


class Runner:
    def __init__(self, brain: Brain, tools: list | None = None, conversation_id: str = "default", history_turns: int = 0):
        self.brain = brain
        self.history: list[dict] = []
        self.tools: dict = {t.name: t for t in (tools or [])}
        self.log = EventLog(Path("conversations") / conversation_id)
        self.history = _rebuild_history(self.log.load(last_n=history_turns))

    def send(self, message: str) -> None:
        self.history.append({"role": "user", "content": message})
        self.log.append(MessageEvent(role="user", content=message))

    def run(self) -> str | None:
        while True:
            response = self.brain.call(self.history)

            if response.type == "content":
                self.history.append({"role": "assistant", "content": response.content})
                self.log.append(MessageEvent(role="assistant", content=response.content))
                print(f"Assistant: {response.content}")
                return response.content

            elif response.type == "tool_call":
                self.history.append({
                    "role": "assistant",
                    "tool_calls": [tc.model_dump() for tc in response.tool_calls],
                })

                for tc in response.tool_calls:
                    tool_name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    print(f"[tool call: {tool_name}({args})]")

                    self.log.append(ActionEvent(
                        tool_name=tool_name,
                        args=args,
                        tool_call_id=tc.id,
                    ))

                    tool = self.tools.get(tool_name)
                    if tool is None:
                        result = f"Error: unknown tool '{tool_name}'"
                        self.log.append(ObservationEvent(
                            tool_call_id=tc.id,
                            output=result,
                            exit_code=1,
                            is_error=True,
                        ))
                    else:
                        action = tool.build_action(args)
                        observation = tool.run(action)
                        prefix = "[ERROR] " if observation.is_error else ""
                        result = f"{prefix}{observation.output}\n[exit code: {observation.exit_code}]"
                        print(f"[output: {observation.output.strip() or '(empty)'}]")
                        print(f"[exit code: {observation.exit_code}{'  ERROR' if observation.is_error else ''}]")

                        self.log.append(ObservationEvent(
                            tool_call_id=tc.id,
                            output=observation.output,
                            exit_code=observation.exit_code,
                            is_error=observation.is_error,
                        ))

                    self.history.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })

            elif response.type == "reasoning":
                print("[reasoning only — nudging model]")
                self.history.append({"role": "user", "content": NUDGE})

            elif response.type == "empty":
                print("[empty response — nudging model]")
                self.history.append({"role": "user", "content": NUDGE})