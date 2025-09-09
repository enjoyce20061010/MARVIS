from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional


class JsonlTracer:
    def __init__(self, path: str = "trace.jsonl"):
        self.path = path

    def log(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        record = {
            "ts": int(time.time() * 1000),
            "event": event,
            **(payload or {}),
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


