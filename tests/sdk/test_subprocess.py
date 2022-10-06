import string

from substra.sdk.backends.local.compute.spawner.subprocess import _get_command_args


def test_get_command_args_without_space():
    # check that it's not changing the path if there is no spaces
    function_name = "train"
    command = ["--opener-path", "${_VOLUME_OPENER}", "--compute-plan-path", "${_VOLUME_LOCAL}"]
    command_template = [string.Template(part) for part in command]
    local_volumes = {
        "_VOLUME_OPENER": "/a/path/without/any/space/opener.py",
        "_VOLUME_LOCAL": "/another/path/without/any/space",
    }

    py_commands = _get_command_args(function_name, command_template, local_volumes)

    valid_py_commands = [
        "--function-name",
        "train",
        "--opener-path",
        "/a/path/without/any/space/opener.py",
        "--compute-plan-path",
        "/another/path/without/any/space",
    ]

    assert py_commands == valid_py_commands


def test_get_command_args_with_spaces():
    # check that it's not splitting path with spaces in different arguments
    function_name = "train"
    command = ["--opener-path", "${_VOLUME_OPENER}", "--compute-plan-path", "${_VOLUME_LOCAL}"]
    command_template = [string.Template(part) for part in command]
    local_volumes = {
        "_VOLUME_OPENER": "/a/path with spaces/opener.py",
        "_VOLUME_LOCAL": "/another/path with spaces",
    }

    py_commands = _get_command_args(function_name, command_template, local_volumes)

    valid_py_commands = [
        "--function-name",
        "train",
        "--opener-path",
        "/a/path with spaces/opener.py",
        "--compute-plan-path",
        "/another/path with spaces",
    ]

    assert py_commands == valid_py_commands
