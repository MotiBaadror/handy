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
max_messages = int(os.getenv("MAX_MESSAGES", "20"))
keep_first = int(os.getenv("KEEP_FIRST", "1"))
max_iterations = int(os.getenv("MAX_ITERATIONS", "50"))

tools = resolve_tools()

brain = Brain(
    model=os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile"),
    api_key=os.getenv("LLM_API_KEY", ""),
    tools=[t.schema for t in tools],
)

secrets = SecretRegistry()
secrets.set("MY_TOKEN", os.getenv("MY_TOKEN", ""))

runner = Runner(brain=brain, tools=tools, conversation_id=conversation_id, secrets=secrets, max_messages=max_messages, keep_first=keep_first, max_iterations=max_iterations)

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