from enum import StrEnum


class ResponseType(StrEnum):
    TOOL_CALL = "tool_call"
    CONTENT = "content"
    EMPTY = "empty"
