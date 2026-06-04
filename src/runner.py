import json
from pathlib import Path

from .brain import Brain
from .condenser import Condenser
from .events import ActionEvent, CondensationEvent, Event, EventLog, MessageEvent, ObservationEvent
from .secrets import SecretRegistry

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
        elif isinstance(event, CondensationEvent):
            history.append({"role": "user", "content": f"[Summary of earlier conversation]: {event.summary}"})
            i += 1
    return history


class Runner:
    def __init__(self, brain: Brain, tools: list | None = None, conversation_id: str = "default", secrets: SecretRegistry | None = None, max_messages: int = 20, keep_first: int = 1, max_iterations: int = 50, base_dir: Path = Path("conversations")):
        self.brain = brain
        self.history: list[dict] = []
        self.tools: dict = {t.name: t for t in (tools or [])}
        self.log = EventLog(base_dir / conversation_id)
        self.history = _rebuild_history(self.log.load(keep_first=keep_first))
        self.secrets = secrets or SecretRegistry()
        self.condenser = Condenser(brain, log=self.log, max_messages=max_messages, keep_first=keep_first)
        self.max_iterations = max_iterations

    def send(self, message: str) -> None:
        self.history.append({"role": "user", "content": message})
        self.log.append(MessageEvent(role="user", content=message))

    def _parse_args(self, tc) -> dict:
        """Parse JSON arguments from a tool call. Raises json.JSONDecodeError on bad input."""
        return json.loads(tc.function.arguments)

    def _execute_tool(self, tool, args: dict, tool_call_id: str) -> str:
        """Build action, run tool, mask output, log observation. Returns result string."""
        action = tool.build_action(args)
        observation = tool.run(action, env=self.secrets.as_env())
        masked_output = self.secrets.mask(observation.output)
        prefix = "[ERROR] " if observation.is_error else ""
        result = f"{prefix}{masked_output}\n[exit code: {observation.exit_code}]"
        print(f"[output: {masked_output.strip() or '(empty)'}]")
        print(f"[exit code: {observation.exit_code}{'  ERROR' if observation.is_error else ''}]")
        self.log.append(ObservationEvent(
            tool_call_id=tool_call_id,
            output=masked_output,
            exit_code=observation.exit_code,
            is_error=observation.is_error,
        ))
        return result

    def _handle_tool_call(self, tc) -> str:
        """Handle one tool call end-to-end. Returns result string, never raises."""
        tool_name = tc.function.name

        try:
            args = self._parse_args(tc)
        except Exception as e:
            result = f"Error: could not parse tool arguments — {e}"
            self.log.append(ObservationEvent(tool_call_id=tc.id, output=result, exit_code=1, is_error=True))
            return result

        print(f"[tool call: {tool_name}({args})]")
        self.log.append(ActionEvent(tool_name=tool_name, args=args, tool_call_id=tc.id))

        tool = self.tools.get(tool_name)
        if tool is None:
            result = f"Error: unknown tool '{tool_name}'"
            self.log.append(ObservationEvent(tool_call_id=tc.id, output=result, exit_code=1, is_error=True))
            return result

        try:
            return self._execute_tool(tool, args, tc.id)
        except Exception as e:
            result = f"Error: tool execution failed — {e}"
            self.log.append(ObservationEvent(tool_call_id=tc.id, output=result, exit_code=1, is_error=True))
            return result

    def run(self) -> str | None:
        self.history = self.condenser.maybe_condense(self.history)
        iteration = 0
        while True:
            if iteration >= self.max_iterations:
                print(f"[max iterations ({self.max_iterations}) reached — stopping]")
                return None
            iteration += 1
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
                    result = self._handle_tool_call(tc)
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