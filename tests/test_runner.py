import pytest
from unittest.mock import MagicMock, patch
from src.brain import Brain, Response
from src.runner import Runner
from src.tools import ShellTool


@pytest.fixture
def runner(tmp_path):
    brain = Brain(model="fake/model", api_key="fake-key")
    return Runner(
        brain=brain,
        tools=[ShellTool()],
        conversation_id="test",
        base_dir=tmp_path,
    )


def make_tool_call(name: str, arguments: str) -> MagicMock:
    tc = MagicMock()
    tc.id = "call_001"
    tc.function.name = name
    tc.function.arguments = arguments
    tc.model_dump.return_value = {
        "id": "call_001",
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }
    return tc


def make_tool_response(name: str, arguments: str) -> Response:
    return Response(type="tool_call", tool_calls=[make_tool_call(name, arguments)])


def make_content_response(text: str) -> Response:
    return Response(type="content", content=text)


def test_invalid_json_arguments_does_not_crash(runner):
    with patch.object(runner.brain, "call") as mock_call:
        mock_call.side_effect = [
            make_tool_response("shell", "not valid json {{{"),
            make_content_response("I made an error, sorry."),
        ]
        runner.send("list files")
        result = runner.run()
    assert result == "I made an error, sorry."


def test_wrong_tool_arguments_does_not_crash(runner):
    with patch.object(runner.brain, "call") as mock_call:
        mock_call.side_effect = [
            make_tool_response("shell", '{"wrong_key": "value"}'),
            make_content_response("I used wrong arguments, let me fix that."),
        ]
        runner.send("list files")
        result = runner.run()
    assert result == "I used wrong arguments, let me fix that."


def test_unknown_tool_does_not_crash(runner):
    with patch.object(runner.brain, "call") as mock_call:
        mock_call.side_effect = [
            make_tool_response("nonexistent_tool", '{"command": "ls"}'),
            make_content_response("That tool does not exist."),
        ]
        runner.send("do something")
        result = runner.run()
    assert result == "That tool does not exist."