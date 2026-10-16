import json

import pytest

from blurb_length_adapter.core import evaluate, load_workspace, render_markdown


@pytest.mark.parametrize("mode,count", [("all", 9), ("exclude-whitespace", 5)])
def test_character_policies(tmp_path, mode, count):
    text = "A\tB\n\u00a0\u2003😀e\u0301"
    data = {
        "version": 1,
        "source": "source",
        "profiles": [
            {
                "id": "p",
                "label": "P",
                "max_characters": count,
                "max_words": 4,
                "character_count": mode,
            }
        ],
        "variants": {"p": text},
    }
    path = tmp_path / "workspace.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate(load_workspace(path))
    row = result["profiles"][0]
    assert row["status"] == "within-limit"
    assert row["character_count"] == mode
    assert row["counted_characters"] == count
    assert mode in render_markdown(result)
    data["profiles"][0]["max_characters"] = count - 1
    assert evaluate(data)["profiles"][0]["status"] == "over-limit"
    data["profiles"][0]["max_words"] = 1
    assert "words over" in evaluate(data)["profiles"][0]["violations"][0]


@pytest.mark.parametrize("mode", ["spaces", "", None, 1, [], {}])
def test_invalid_character_policy(tmp_path, mode):
    data = {
        "version": 1,
        "source": "x",
        "profiles": [{"id": "p", "label": "P", "max_words": 1, "character_count": mode}],
    }
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="character_count"):
        load_workspace(path)
    with pytest.raises(ValueError, match="character_count"):
        evaluate(data)


def test_default_policy_and_zero_width():
    data = {
        "source": "x",
        "profiles": [{"id": "p", "label": "P", "max_characters": 2}],
        "variants": {"p": "x y"},
    }
    assert evaluate(data)["profiles"][0]["status"] == "over-limit"
    data["profiles"][0]["character_count"] = "exclude-whitespace"
    data["variants"]["p"] = "x\u200by"
    assert evaluate(data)["profiles"][0]["counted_characters"] == 3
