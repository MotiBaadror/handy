import os
from dotenv import load_dotenv
from src.brain import Brain
from src.runner import Runner
from src.tools import ShellTool

load_dotenv()

brain = Brain(
    model=os.getenv("LLM_MODEL", "groq/llama-3.1-8b-instant"),
    api_key=os.getenv("GROQ_API_KEY", ""),
    tools=[ShellTool.schema],
)

runner = Runner(brain=brain)
runner.send("Count how many Python files are in the current directory.")
runner.run()
