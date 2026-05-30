import os


class SecretRegistry:
    def __init__(self):
        self._secrets: dict[str, str] = {}

    def set(self, name: str, value: str) -> None:
        self._secrets[name] = value

    def names(self) -> list[str]:
        return list(self._secrets.keys())

    def as_env(self) -> dict[str, str]:
        return {**os.environ, **self._secrets}

    def mask(self, text: str) -> str:
        for value in self._secrets.values():
            if value and value in text:
                text = text.replace(value, "<secret-hidden>")
        return text