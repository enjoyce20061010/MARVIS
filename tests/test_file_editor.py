import glob
import os

from core.file_editor import FileEditor


def test_write_and_backup_and_diff(tmp_path, monkeypatch):
    # restrict root to tmp
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        editor = FileEditor(root=".")

        # initial write
        editor.write_file("tests/sample.txt", "hello")
        assert os.path.exists("tests/sample.txt")

        # preview diff for change
        diff = editor.preview_diff("tests/sample.txt", "hello world")
        assert "-hello" in diff and "+hello world" in diff

        # replace triggers backup
        editor.replace_text("tests/sample.txt", "hello", "hello world")
        backups = glob.glob("tests/sample.txt.bak.*")
        assert backups, "expected at least one backup file"

        # delete triggers backup
        editor.delete_file("tests/sample.txt")
        backups2 = glob.glob("tests/sample.txt.bak.*")
        assert len(backups2) >= len(backups)
    finally:
        os.chdir(cwd)


