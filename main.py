import os
from dotenv import load_dotenv
from src.brain import Brain
from src.runner import Runner

load_dotenv()

brain = Brain(
    model=os.getenv("LLM_MODEL", "groq/llama-3.1-8b-instant"),
    api_key=os.getenv("GROQ_API_KEY", ""),
)

runner = Runner(brain=brain)
runner.send("What is 2 + 2? Answer in one sentence.")
runner.run()
