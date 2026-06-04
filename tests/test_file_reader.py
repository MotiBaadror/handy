import pytest
from unittest.mock import patch
from src.tools import FileReaderAction, FileReaderTool


@pytest.fixture
def tool():
    return FileReaderTool()


def test_reads_file_with_line_numbers(tool, tmp_path):
    f = tmp_path / "hello.txt"
    f.write_text("line one\nline two\nline three")

    with patch("src.tools.Path.cwd", return_value=tmp_path):
        obs = tool.run(FileReaderAction(path="hello.txt"))

    assert not obs.is_error
    assert "1" in obs.output
    assert "line one" in obs.output
    assert "2" in obs.output
    assert "line two" in obs.output


def test_file_not_found(tool, tmp_path):
    with patch("src.tools.Path.cwd", return_value=tmp_path):
        obs = tool.run(FileReaderAction(path="nonexistent.txt"))

    assert obs.is_error
    assert "not found" in obs.output


def test_directory_not_allowed(tool, tmp_path):
    subdir = tmp_path / "mydir"
    subdir.mkdir()

    with patch("src.tools.Path.cwd", return_value=tmp_path):
        obs = tool.run(FileReaderAction(path="mydir"))

    assert obs.is_error
    assert "directory" in obs.output


def test_path_traversal_blocked(tool, tmp_path):
    with patch("src.tools.Path.cwd", return_value=tmp_path):
        obs = tool.run(FileReaderAction(path="../../etc/passwd"))

    assert obs.is_error
    assert "access denied" in obs.output


def test_build_action(tool):
    action = tool.build_action({"path": "src/main.py"})
    assert isinstance(action, FileReaderAction)
    assert action.path == "src/main.py"