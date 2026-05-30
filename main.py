import os
import sys
from dotenv import load_dotenv
from src.brain import Brain
from src.runner import Runner
from src.registry import resolve_tools
from src.secrets import SecretRegistry
import src.tools  # noqa: F401 — triggers register_tool() at import

load_dotenv()

conversation_id = sys.argv[1] if len(sys.argv) > 1 else "default"
history_turns = int(os.getenv("HISTORY_TURNS", "0"))

tools = resolve_tools()

brain = Brain(
    model=os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile"),
    api_key=os.getenv("LLM_API_KEY", ""),
    tools=[t.schema for t in tools],
)

secrets = SecretRegistry()
secrets.set("MY_TOKEN", os.getenv("MY_TOKEN", ""))

runner = Runner(brain=brain, tools=tools, conversation_id=conversation_id, history_turns=history_turns, secrets=secrets)

print(f"[conversation: {conversation_id}] [{len(runner.history)} messages loaded]\n")

while True:
    try:
        user_input = input("> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBye.")
        break

    if not user_input:
        continue
    if user_input.lower() == "exit":
        break

    runner.send(user_input)
    runner.run()
    print()