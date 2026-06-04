import subprocess
from dataclasses import dataclass
from pathlib import Path
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

    def run(self, action: ShellAction, env: dict | None = None) -> ShellObservation:
        result = subprocess.run(
            action.command,
            shell=True,
            capture_output=True,
            text=True,
            env=env,
        )
        is_error = result.returncode != 0
        output = result.stderr if is_error else result.stdout
        return ShellObservation(output=output, exit_code=result.returncode, is_error=is_error)


register_tool(ShellTool())


@dataclass
class FileReaderAction:
    path: str


@dataclass
class FileReaderObservation:
    output: str
    is_error: bool


class FileReaderTool:
    name = "file_reader"
    description = "Read a file from the current working directory."
    schema = {
        "type": "function",
        "function": {
            "name": "file_reader",
            "description": "Read a file from the current working directory. Cannot access files outside it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file from the current working directory.",
                    }
                },
                "required": ["path"],
            },
        },
    }

    def build_action(self, args: dict) -> FileReaderAction:
        return FileReaderAction(**args)

    def run(self, action: FileReaderAction, env: dict | None = None) -> FileReaderObservation:
        cwd = Path.cwd()
        target = (cwd / action.path).resolve()

        if not target.is_relative_to(cwd):
            return FileReaderObservation(
                output=f"Error: access denied — '{action.path}' is outside the working directory",
                is_error=True,
            )

        if not target.exists():
            return FileReaderObservation(
                output=f"Error: file not found — '{action.path}'",
                is_error=True,
            )

        if not target.is_file():
            return FileReaderObservation(
                output=f"Error: '{action.path}' is a directory, not a file",
                is_error=True,
            )

        content = target.read_text(errors="replace")
        lines = content.splitlines()
        numbered = "\n".join(f"{i+1:4d}  {line}" for i, line in enumerate(lines))
        return FileReaderObservation(output=numbered, is_error=False)


register_tool(FileReaderTool())
