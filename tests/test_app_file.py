import pathlib


def test_app_contains_title():
    repo_root = pathlib.Path(__file__).parent.parent
    app_py = repo_root / "app.py"
    content = app_py.read_text(encoding="utf-8")
    assert "VoiceNotes AI" in content
