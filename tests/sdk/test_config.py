import pytest

import substra.sdk.config as configuration


def test_add_load_profile(tmpdir):
    path = tmpdir / 'substra.cfg'
    manager = configuration.Manager(str(path))

    profile_1 = manager.add_profile(
        'owkin',
        url='http://owkin.substra-backend:8000',
        version='0.0')

    profile_2 = manager.load_profile('owkin')
    assert profile_1 == profile_2


def test_load_profile_fail(tmpdir):
    path = tmpdir / 'substra.cfg'
    manager = configuration.Manager(str(path))

    with pytest.raises(FileNotFoundError):
        manager.load_profile('notfound')

    manager.add_profile('default')

    with pytest.raises(configuration.ProfileNotFoundError):
        manager.load_profile('notfound')
