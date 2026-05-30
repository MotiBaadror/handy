import os
from dotenv import load_dotenv
from src.brain import Brain
from src.runner import Runner
from src.registry import resolve_tools
import src.tools  # noqa: F401 — triggers register_tool() at import

load_dotenv()

tools = resolve_tools()

brain = Brain(
    model=os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile"),
    api_key=os.getenv("LLM_API_KEY", ""),
    tools=[t.schema for t in tools],
)

runner = Runner(brain=brain, tools=tools)
runner.send("Count how many Python files are in the current directory.")
runner.run()
