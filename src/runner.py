import json
from .brain import Brain

NUDGE = (
    "Your last response was empty. "
    "Please reply with something useful."
)


class Runner:
    def __init__(self, brain: Brain, tools: list | None = None):
        self.brain = brain
        self.history: list[dict] = []
        self.tools: dict = {t.name: t for t in (tools or [])}

    def send(self, message: str) -> None:
        self.history.append({"role": "user", "content": message})

    def run(self) -> str | None:
        while True:
            response = self.brain.call(self.history)

            if response.type == "content":
                self.history.append({"role": "assistant", "content": response.content})
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

                    tool = self.tools.get(tool_name)
                    if tool is None:
                        result = f"Error: unknown tool '{tool_name}'"
                    else:
                        action = tool.build_action(args)
                        observation = tool.run(action)
                        prefix = "[ERROR] " if observation.is_error else ""
                        result = f"{prefix}{observation.output}\n[exit code: {observation.exit_code}]"
                        print(f"[output: {observation.output.strip() or '(empty)'}]")
                        print(f"[exit code: {observation.exit_code}{'  ERROR' if observation.is_error else ''}]")

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
