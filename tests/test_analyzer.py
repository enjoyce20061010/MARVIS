import json

from modules.analyzer import SystemAnalyzer


def test_analyzer_returns_json_with_whitelisted_files():
    analyzer = SystemAnalyzer()
    raw = analyzer.summarize_context("demo task")
    data = json.loads(raw)

    assert "task" in data and data["task"] == "demo task"
    assert "files" in data and isinstance(data["files"], list)

    # ensure all files are within whitelist
    for fi in data["files"]:
        assert any(
            fi["path"].startswith(prefix + "/") or fi["path"].startswith(prefix)
            for prefix in ("adapters", "core", "modules", "tests")
        )
        assert isinstance(fi["imports"], list)


