import json
from pathlib import Path

import pytest

from blurb_length_adapter.cli import main


def source_file(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(
        json.dumps(
            {
                "version": 1,
                "source": "Source",
                "profiles": [{"id": "p", "label": "P", "max_words": 2}],
            }
        ),
        encoding="utf-8",
    )
    return source


def test_source_and_existing_outputs_are_preserved(tmp_path, capsys):
    source = source_file(tmp_path)
    original = source.read_bytes()
    assert main([str(source), "--output", str(source)]) == 2
    assert source.read_bytes() == original
    output = tmp_path / "report"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2
    assert output.read_text(encoding="utf-8") == "keep"
    assert "already exists" in capsys.readouterr().err


@pytest.mark.parametrize("loop", [False, True])
def test_symlink_destinations_are_refused(tmp_path, loop):
    source = source_file(tmp_path)
    output = tmp_path / "report"
    target = output if loop else tmp_path / "missing"
    try:
        output.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")
    assert main([str(source), "--output", str(output)]) == 2
    assert output.is_symlink()
    if not loop:
        assert not target.exists()


def test_concurrent_creator_is_preserved(tmp_path, monkeypatch):
    source = source_file(tmp_path)
    output = tmp_path / "report"
    original_open = Path.open

    def concurrent_open(path, mode="r", *args, **kwargs):
        if path == output and mode == "x":
            with original_open(path, "w", encoding="utf-8") as other:
                other.write("created by another writer")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", concurrent_open)
    assert main([str(source), "--output", str(output)]) == 2
    assert output.read_text(encoding="utf-8") == "created by another writer"


def test_new_output_and_actionable_io_error(tmp_path, capsys):
    source = source_file(tmp_path)
    output = tmp_path / "report"
    assert main([str(source), "--output", str(output)]) == 0
    assert output.read_bytes().endswith(b"\n")
    assert b"\r\n" not in output.read_bytes()
    assert main([str(source), "--output", str(tmp_path / "missing" / "report")]) == 2
    assert "error:" in capsys.readouterr().err
    assert main([str(tmp_path / "absent")]) == 2
    assert "error:" in capsys.readouterr().err
