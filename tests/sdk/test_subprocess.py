import string
import sys
import tempfile
from pathlib import Path

from substra.sdk.backends.local.compute.spawner.subprocess import _get_py_command


def test_get_py_command_without_space():
    # check that it's not changing the path if there is no spaces
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
        tmpdir = Path(tmpdir)
        script_name = "algo.py"
        method_name = "train"
        command = "--opener-path ${_VOLUME_OPENER} --compute-plan-path ${_VOLUME_LOCAL}"
        command_template = string.Template(command)
        local_volumes = {
            "_VOLUME_OPENER": "/a/path/without/any/space/opener.py",
            "_VOLUME_LOCAL": "/another/path/without/any/space",
        }

        py_commands = _get_py_command(script_name, method_name, tmpdir, command_template, local_volumes)

        valid_py_commands = [
            sys.executable,
            str(tmpdir / script_name),
            "--method-name",
            "train",
            "--opener-path",
            "/a/path/without/any/space/opener.py",
            "--compute-plan-path",
            "/another/path/without/any/space",
        ]

        assert py_commands == valid_py_commands


def test_get_py_command_with_spaces():
    # check that it's not splitting path with spaces in different arguments
    with tempfile.TemporaryDirectory(dir=Path.cwd()) as tmpdir:
        tmpdir = Path(tmpdir)
        script_name = "algo.py"
        method_name = "train"
        command = "--opener-path ${_VOLUME_OPENER} --compute-plan-path ${_VOLUME_LOCAL}"
        command_template = string.Template(command)
        local_volumes = {
            "_VOLUME_OPENER": "/a/path with spaces/opener.py",
            "_VOLUME_LOCAL": "/another/path with spaces",
        }

        py_commands = _get_py_command(script_name, method_name, tmpdir, command_template, local_volumes)

        valid_py_commands = [
            sys.executable,
            str(tmpdir / script_name),
            "--method-name",
            "train",
            "--opener-path",
            "/a/path with spaces/opener.py",
            "--compute-plan-path",
            "/another/path with spaces",
        ]

        assert py_commands == valid_py_commands
