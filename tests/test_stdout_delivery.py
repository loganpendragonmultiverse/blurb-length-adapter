import os
import subprocess
import sys
from pathlib import Path

import pytest
from test_output_safety import source_file

import blurb_length_adapter as package
from blurb_length_adapter import cli


def run_cli(source, **kwargs):
    env = dict(
        os.environ, PYTHONPATH=str(Path(package.__file__).parent.parent), PYTHONIOENCODING="utf-8"
    )
    return subprocess.run(
        [sys.executable, "-m", "blurb_length_adapter", str(source)],
        check=False,
        env=env,
        stderr=subprocess.PIPE,
        **kwargs,
    )


@pytest.mark.parametrize("large", [False, True])
def test_closed_pipe_returns_two_without_shutdown_error(tmp_path, large):
    source = source_file(tmp_path)
    if large:
        import json

        data = json.loads(source.read_text())
        data["source"] = "é😀" * 100_001
        source.write_text(json.dumps(data))
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    try:
        result = run_cli(source, stdout=write_fd)
    finally:
        os.close(write_fd)
    assert result.returncode == 2
    assert b"error:" in result.stderr
    assert b"Exception ignored" not in result.stderr
    assert b"Traceback" not in result.stderr


@pytest.mark.parametrize("large", [False, True])
def test_normal_stdout_is_complete_and_matches_file(tmp_path, large):
    source = source_file(tmp_path)
    if large:
        import json

        data = json.loads(source.read_text())
        data["source"] = "é😀" * 100_001
        source.write_text(json.dumps(data))
    result = run_cli(source, stdout=subprocess.PIPE)
    assert result.returncode == 0
    assert not result.stderr
    output = tmp_path / "report"
    assert cli.main([str(source), "--output", str(output)]) == 0
    assert result.stdout == output.read_bytes()
    if large:
        assert len(result.stdout) > 200_000


def test_descriptor_partial_writes_and_zero_progress(monkeypatch):
    class Descriptor:
        encoding = "utf-8"
        errors = "strict"

        def fileno(self):
            return 123

    monkeypatch.setattr(cli.sys, "stdout", Descriptor())
    accepted = bytearray()

    def partial_write(descriptor, data):
        assert descriptor == 123
        piece = data[:3]
        accepted.extend(piece)
        return len(piece)

    monkeypatch.setattr(cli.os, "write", partial_write)
    cli._write_stdout("é😀\ncomplete")
    assert accepted == "é😀\ncomplete".encode()
    monkeypatch.setattr(cli.os, "write", lambda descriptor, data: 0)
    with pytest.raises(OSError, match="no report bytes"):
        cli._write_stdout("x")
