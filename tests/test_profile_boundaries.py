import json

import pytest

from blurb_length_adapter.cli import main
from blurb_length_adapter.core import evaluate, load_workspace, metrics


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", ""),
        ("id", " "),
        ("label", ""),
        ("label", "\t"),
        ("max_words", True),
        ("max_words", False),
        ("max_characters", True),
        ("max_characters", False),
    ],
)
def test_reject_invalid_profiles(tmp_path, capsys, field, value):
    profile = {"id": "p", "label": "P", "max_words": 2, "max_characters": 20}
    profile[field] = value
    source = tmp_path / "workspace.json"
    source.write_text(json.dumps({"version": 1, "source": "Source", "profiles": [profile]}))
    output = tmp_path / "report.json"
    assert main([str(source), "--format", "json", "--output", str(output)]) == 2
    assert "error:" in capsys.readouterr().err
    assert not output.exists()
    with pytest.raises(ValueError):
        load_workspace(source)


@pytest.mark.parametrize("text", ["A\tB\n\u00a0\u2003😀e\u0301", "👩‍🚀", "a\u200bb", "one two"])
@pytest.mark.parametrize("mode", ["all", "exclude-whitespace"])
def test_unicode_exact_and_one_over(tmp_path, text, mode):
    counted = len(text) if mode == "all" else sum(not c.isspace() for c in text)
    data = {
        "version": 1,
        "source": text,
        "profiles": [{"id": "p", "label": "P", "max_characters": counted, "character_count": mode}],
        "variants": {"p": text},
    }
    path = tmp_path / "workspace.json"
    path.write_text(json.dumps(data))
    row = evaluate(load_workspace(path))["profiles"][0]
    assert row["counted_characters"] == counted
    assert row["status"] == "within-limit"
    assert row["text"] == text
    data["profiles"][0]["max_characters"] = counted - 1
    path.write_text(json.dumps(data))
    assert evaluate(load_workspace(path))["profiles"][0]["status"] == "over-limit"
    assert metrics(text)["words"] == len(text.split())
