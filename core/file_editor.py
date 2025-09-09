from __future__ import annotations

import difflib
import os
import shutil
from datetime import datetime


WHITELIST = {"modules", "tests"}


class FileEditor:
    def __init__(self, root: str = "."):
        self.root = root

    def _is_allowed(self, path: str) -> bool:
        norm = os.path.normpath(path).lstrip("./")
        return any(norm == d or norm.startswith(d + "/") for d in WHITELIST)

    def _abs(self, path: str) -> str:
        return os.path.join(self.root, path)

    def _backup(self, abs_path: str) -> None:
        if os.path.exists(abs_path):
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_path = abs_path + f".bak.{ts}"
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(abs_path, backup_path)

    def preview_diff(self, path: str, new_content: str) -> str:
        if not self._is_allowed(path):
            raise PermissionError(f"Path not allowed: {path}")
        abs_path = self._abs(path)
        old = ""
        if os.path.exists(abs_path):
            with open(abs_path, "r", encoding="utf-8") as f:
                old = f.read()
        diff = difflib.unified_diff(
            old.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=path,
            tofile=path,
        )
        return "".join(diff)

    def write_file(self, path: str, content: str) -> None:
        if not self._is_allowed(path):
            raise PermissionError(f"Path not allowed: {path}")
        abs_path = self._abs(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        # backup existing
        self._backup(abs_path)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

    def replace_text(self, path: str, find: str, replace: str) -> None:
        if not self._is_allowed(path):
            raise PermissionError(f"Path not allowed: {path}")
        abs_path = self._abs(path)
        with open(abs_path, "r", encoding="utf-8") as f:
            data = f.read()
        new_data = data.replace(find, replace)
        # backup before overwrite
        self._backup(abs_path)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_data)

    def delete_file(self, path: str) -> None:
        if not self._is_allowed(path):
            raise PermissionError(f"Path not allowed: {path}")
        abs_path = self._abs(path)
        if os.path.exists(abs_path):
            # backup before delete
            self._backup(abs_path)
            os.remove(abs_path)


