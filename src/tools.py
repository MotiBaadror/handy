import subprocess
from dataclasses import dataclass
from .registry import register_tool


@dataclass
class ShellAction:
    command: str


@dataclass
class ShellObservation:
    output: str
    exit_code: int
    is_error: bool


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

    def build_action(self, args: dict) -> ShellAction:
        return ShellAction(**args)

    def run(self, action: ShellAction) -> ShellObservation:
        result = subprocess.run(
            action.command,
            shell=True,
            capture_output=True,
            text=True,
        )
        is_error = result.returncode != 0
        output = result.stderr if is_error else result.stdout
        return ShellObservation(output=output, exit_code=result.returncode, is_error=is_error)


register_tool(ShellTool())
