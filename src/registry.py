_REGISTRY: dict[str, object] = {}


def register_tool(tool) -> None:
    _REGISTRY[tool.name] = tool


def resolve_tools() -> list:
    return list(_REGISTRY.values())
