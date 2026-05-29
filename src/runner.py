from .brain import Brain

NUDGE = (
    "Your last response was empty. "
    "Please reply with something useful."
)


class Runner:
    def __init__(self, brain: Brain):
        self.brain = brain
        self.history: list[dict] = []

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
                # tool execution not implemented yet — coming in next step
                print("[tool call received — not implemented yet]")
                return None

            elif response.type == "reasoning":
                # model is mid-thought, no visible content yet — nudge and loop again
                print("[reasoning only — nudging model]")
                self.history.append({"role": "user", "content": NUDGE})

            elif response.type == "empty":
                # completely empty response — nudge and loop again
                print("[empty response — nudging model]")
                self.history.append({"role": "user", "content": NUDGE})
