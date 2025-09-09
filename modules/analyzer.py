from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, List


PY_WHITELIST_DIRS = {"adapters", "core", "modules", "tests"}


@dataclass
class FileInfo:
    path: str
    imports: List[str]


class SystemAnalyzer:
    def summarize_context(self, task: str) -> str:
        files: List[FileInfo] = []
        import_pattern = re.compile(r"^(from\s+[\w\.]+\s+import\s+[\w\*,\s]+|import\s+[\w\.,\s]+)")

        for root, _, filenames in os.walk("."):
            # enforce whitelist
            parts = os.path.normpath(root).lstrip("./").split(os.sep)
            if parts and parts[0] not in PY_WHITELIST_DIRS:
                continue
            for name in filenames:
                if not name.endswith(".py"):
                    continue
                rel_path = os.path.join(root, name)
                try:
                    with open(rel_path, "r", encoding="utf-8") as f:
                        imports: List[str] = []
                        for line in f:
                            m = import_pattern.match(line.strip())
                            if m:
                                imports.append(m.group(0))
                    files.append(FileInfo(path=rel_path.lstrip("./"), imports=imports))
                except Exception:
                    # best-effort scanning; skip unreadable files
                    continue

        summary: Dict[str, object] = {
            "task": task,
            "files": [asdict(fi) for fi in files],
        }
        return json.dumps(summary, ensure_ascii=False)
