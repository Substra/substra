import sys

import pytest

from substratools import exceptions
from substratools.opener import Opener
from substratools.utils import get_logger
from substratools.utils import import_module
from substratools.utils import load_interface_from_module


def test_invalid_interface():
    code = """
def score():
    pass
"""
    import_module("score", code)
    with pytest.raises(exceptions.InvalidInterfaceError):
        load_interface_from_module("score", interface_class=Opener)


@pytest.fixture
def syspaths():
    copy = sys.path[:]
    yield sys.path
    sys.path = copy


def test_empty_module(tmpdir, syspaths):
    with tmpdir.as_cwd():
        # python allows to import an empty directoy
        # check that the error message would be helpful for debugging purposes
        tmpdir.mkdir("foomod")
        syspaths.append(str(tmpdir))

        with pytest.raises(exceptions.EmptyInterfaceError):
            load_interface_from_module("foomod", interface_class=Opener)


def test_get_logger(capfd):
    logger = get_logger("test")
    logger.info("message")
    captured = capfd.readouterr()
    assert "INFO   substratools.test - message" in captured.err
