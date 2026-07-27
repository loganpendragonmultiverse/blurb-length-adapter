import json

import pytest

from blurb_length_adapter.cli import main
from blurb_length_adapter.core import evaluate, load_workspace, metrics, render_markdown


def workspace():
    return {
        "version": 1,
        "source": "A courier discovers a city hidden beneath the winter sea.",
        "profiles": [
            {"id": "short", "label": "Short listing", "max_words": 8},
            {"id": "store", "label": "Store description", "max_characters": 120},
        ],
        "variants": {"short": "A courier finds a city beneath winter seas."},
    }


def test_metrics_evaluation_and_render():
    assert metrics("one two") == {"words": 2, "characters": 7, "characters_without_spaces": 6}
    result = evaluate(workspace())
    assert result["profiles"][0]["status"] == "within-limit"
    assert result["profiles"][1]["status"] == "missing"
    assert "Write the adapted blurb" in render_markdown(result)
    data = workspace()
    data["variants"]["short"] = "one two three four five six seven eight nine"
    data["variants"]["store"] = "x" * 121
    result = evaluate(data)
    assert all(item["status"] == "over-limit" for item in result["profiles"])
    assert "words over" in result["profiles"][0]["violations"][0]
    assert "characters over" in render_markdown(result)


def test_load_validation(tmp_path):
    path = tmp_path / "workspace.json"
    path.write_text(json.dumps(workspace()), encoding="utf-8")
    assert load_workspace(path)["profiles"][0]["id"] == "short"
    bad = workspace()
    bad["profiles"][0]["max_words"] = 0
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="positive"):
        load_workspace(path)


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        ({"version": 2}, ValueError),
        ({"version": 1, "source": "", "profiles": []}, ValueError),
        ({"version": 1, "source": "A", "profiles": []}, ValueError),
        ({"version": 1, "source": "A", "profiles": [None]}, TypeError),
        (
            {
                "version": 1,
                "source": "A",
                "profiles": [
                    {"id": "a", "label": "A", "max_words": 1},
                    {"id": "a", "label": "Again", "max_words": 2},
                ],
            },
            ValueError,
        ),
        (
            {
                "version": 1,
                "source": "A",
                "profiles": [{"id": "a", "label": "A", "max_words": 1}],
                "variants": {"missing": "text"},
            },
            TypeError,
        ),
    ],
)
def test_rejects_invalid_workspaces(tmp_path, payload, error):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(error):
        load_workspace(path)


def test_cli_json_and_safe_output(tmp_path, capsys):
    source = tmp_path / "workspace.json"
    source.write_text(json.dumps(workspace()), encoding="utf-8")
    assert main([str(source), "--format", "json"]) == 0
    assert '"within-limit"' in capsys.readouterr().out
    output = tmp_path / "worksheet.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2
