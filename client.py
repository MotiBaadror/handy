import os
from dotenv import load_dotenv
from src.brain import Brain
from src.runner import Runner
from src.tools import ShellTool

load_dotenv()

brain = Brain(
    model=os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile"),
    api_key=os.getenv("GROQ_API_KEY", ""),
    tools=[ShellTool.schema],
)

runner = Runner(brain=brain)
runner.history.append({
    "role": "system",
    "content": "You are a concise assistant. Answer directly and briefly. Do not explain commands or steps unless asked.",
})

print("Handy is ready. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "exit":
        break
    runner.send(user_input)
    runner.run()
    print()
