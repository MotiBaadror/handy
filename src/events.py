import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class MessageEvent:
    role: str       # "user" or "assistant"
    content: str
    id: int = 0
    ts: float = 0.0


@dataclass
class ActionEvent:
    tool_name: str
    args: dict
    tool_call_id: str
    id: int = 0
    ts: float = 0.0


@dataclass
class ObservationEvent:
    tool_call_id: str
    output: str
    exit_code: int
    is_error: bool
    id: int = 0
    ts: float = 0.0


Event = MessageEvent | ActionEvent | ObservationEvent


class EventLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self._counter = self._next_id()

    def _next_id(self) -> int:
        existing = sorted(self.path.glob("event_*.json"))
        return len(existing)

    def load(self, last_n: int = 0) -> list[Event]:
        if last_n == 0:
            return []
        files = sorted(self.path.glob("event_*.json"), key=lambda f: int(f.stem.split("_")[1]))
        files = files[-last_n:]
        events = []
        for f in files:
            data = json.loads(f.read_text())
            kind = data.pop("type")
            if kind == "MessageEvent":
                events.append(MessageEvent(**data))
            elif kind == "ActionEvent":
                events.append(ActionEvent(**data))
            elif kind == "ObservationEvent":
                events.append(ObservationEvent(**data))
        return events

    def append(self, event: Event) -> Event:
        event.id = self._counter
        event.ts = time.time()
        filename = self.path / f"event_{self._counter:04d}.json"
        data = {"type": type(event).__name__, **asdict(event)}
        filename.write_text(json.dumps(data, indent=2))
        self._counter += 1
        return event