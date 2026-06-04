import re

_CI = re.IGNORECASE


def check(command: str) -> str | None:
    """Return an error message if the command hits a policy rail, None if safe."""

    # Rail 1 — fetch-to-exec: curl/wget piped to a shell or interpreter
    has_fetch = bool(re.search(r"\b(?:curl|wget)\b", command, _CI))
    has_pipe_to_exec = bool(re.search(
        r"\|\s*(?:ba)?sh\b|\|\s*python[23]?\b|\|\s*perl\b|\|\s*ruby\b",
        command, _CI,
    ))
    if has_fetch and has_pipe_to_exec:
        return "Blocked: network fetch piped to shell/interpreter (fetch-to-exec)"

    # Rail 2 — raw disk write: dd targeting a device or mkfs
    if re.search(r"\bdd\b.{0,100}of=/dev/", command, _CI):
        return "Blocked: raw disk write via dd"
    if re.search(r"\bmkfs\.", command, _CI):
        return "Blocked: filesystem format via mkfs"

    # Rail 3 — catastrophic delete: rm -rf targeting critical paths
    has_recursive_force = bool(re.search(
        r"\brm\s+(?:-[frR]{2,}|-[rR]\s+-f|-f\s+-[rR]"
        r"|--recursive\s+--force|--force\s+--recursive)\b",
        command, _CI,
    ))
    if has_recursive_force:
        if re.search(
            r"\brm\b.{0,60}\s(?:/(?:\s|$|\*)|~/?(?:\s|$)|/(?:etc|usr|var|home|boot)\b)",
            command, _CI,
        ):
            return "Blocked: recursive force-delete targeting critical path"

    return None