import os
import pytest

from core.file_editor import FileEditor


def test_file_editor_rejects_non_whitelisted():
    editor = FileEditor(root=".")
    with pytest.raises(PermissionError):
        editor.write_file("danger/evil.txt", "x")


def test_preview_diff_on_new_file(tmp_path, monkeypatch):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        editor = FileEditor(root=".")
        diff = editor.preview_diff("tests/new.txt", "hello")
        assert "new file" not in diff  # unified_diff without headers still returns content
        assert "+hello" in diff
    finally:
        os.chdir(cwd)


