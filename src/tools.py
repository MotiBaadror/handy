import subprocess
from dataclasses import dataclass


@dataclass
class ShellAction:
    command: str


@dataclass
class ShellObservation:
    output: str
    exit_code: int


class ShellTool:
    name = "shell"
    description = "Run a shell command and return the output."
    schema = {
        "type": "function",
        "function": {
            "name": "shell",
            "description": "Run a shell command and return the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run.",
                    }
                },
                "required": ["command"],
            },
        },
    }

    def run(self, action: ShellAction) -> ShellObservation:
        result = subprocess.run(
            action.command,
            shell=True,
            capture_output=True,
            text=True,
        )
        output = result.stdout or result.stderr
        return ShellObservation(output=output, exit_code=result.returncode)
