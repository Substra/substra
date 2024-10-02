import os

import pytest

from substratools import exceptions
from substratools.opener import Opener
from substratools.opener import OpenerWrapper
from substratools.opener import load_from_module
from substratools.utils import import_module
from substratools.utils import load_interface_from_module
from substratools.workspace import DEFAULT_INPUT_DATA_FOLDER_PATH


@pytest.fixture
def tmp_cwd(tmp_path):
    # create a temporary current working directory
    new_dir = tmp_path / "workspace"
    new_dir.mkdir()

    old_dir = os.getcwd()
    os.chdir(new_dir)

    yield new_dir

    os.chdir(old_dir)


def test_load_opener_not_found(tmp_cwd):
    with pytest.raises(ImportError):
        load_from_module()


def test_load_invalid_opener(tmp_cwd):
    invalid_script = """
def get_data():
    raise NotImplementedError
"""

    import_module("opener", invalid_script)

    with pytest.raises(exceptions.InvalidInterfaceError):
        load_from_module()


def test_load_opener_as_class(tmp_cwd):
    script = """
from substratools import Opener
class MyOpener(Opener):
    def get_data(self, folders):
        return 'data_class'
    def fake_data(self, n_samples):
        return 'fake_data'
"""

    import_module("opener", script)

    o = load_from_module()
    assert o.get_data() == "data_class"


def test_load_opener_from_path(tmp_cwd, valid_opener_code):
    dirpath = tmp_cwd / "myopener"
    dirpath.mkdir()
    path = dirpath / "my_opener.py"
    path.write_text(valid_opener_code)

    interface = load_interface_from_module(
        "opener",
        interface_class=Opener,
        interface_signature=None,  # XXX does not support interface for debugging
        path=path,
    )
    o = OpenerWrapper(interface, workspace=None)
    assert o.get_data()[0] == "X"


def test_opener_check_folders(tmp_cwd):
    script = """
from substratools import Opener
class MyOpener(Opener):
    def get_data(self, folders):
        assert len(folders) == 5
        return 'data_class'
    def fake_data(self, n_samples):
        return 'fake_data_class'
"""

    import_module("opener", script)

    o = load_from_module()

    # create some data folders
    data_root_path = os.path.join(o._workspace._workdir, DEFAULT_INPUT_DATA_FOLDER_PATH)
    data_paths = [os.path.join(data_root_path, str(i)) for i in range(5)]
    [os.makedirs(p) for p in data_paths]

    o._workspace.input_data_folder_paths = data_paths
    assert o.get_data() == "data_class"
