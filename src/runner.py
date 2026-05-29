import json
from .brain import Brain
from .tools import ShellAction, ShellTool

NUDGE = (
    "Your last response was empty. "
    "Please reply with something useful."
)


class Runner:
    def __init__(self, brain: Brain):
        self.brain = brain
        self.history: list[dict] = []
        self.tools: dict[str, ShellTool] = {ShellTool.name: ShellTool()}

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
                # add LLM's tool call to history
                self.history.append({
                    "role": "assistant",
                    "tool_calls": [tc.model_dump() for tc in response.tool_calls],
                })

                # execute each tool call and add results to history
                for tc in response.tool_calls:
                    tool_name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    print(f"[tool call: {tool_name}({args})]")

                    tool = self.tools.get(tool_name)
                    if tool is None:
                        result = f"Error: unknown tool '{tool_name}'"
                    else:
                        action = ShellAction(**args)
                        observation = tool.run(action)
                        result = f"{observation.output}\n[exit code: {observation.exit_code}]"
                        print(f"[output: {observation.output.strip() or '(empty)'}]")
                        print(f"[exit code: {observation.exit_code}]")

                    # feed result back to LLM as tool message
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
