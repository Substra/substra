import pytest
from _pytest.monkeypatch import MonkeyPatch

import substra


@pytest.fixture(scope="session")
def monkeysession():
    # monkeypatch is function-scoped so cannot use it here
    # https://github.com/pytest-dev/pytest/issues/363#issuecomment-406536200
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def docker_clients(monkeysession):
    monkeysession.setenv("DEBUG_SPAWNER", substra.BackendType.LOCAL_DOCKER.value)
    return [substra.Client(debug=True) for _ in range(2)]


@pytest.fixture(scope="session")
def subprocess_clients(monkeysession):
    monkeysession.setenv("DEBUG_SPAWNER", substra.BackendType.LOCAL_SUBPROCESS.value)
    return [substra.Client(debug=True) for _ in range(2)]


@pytest.fixture(scope="session", params=["docker", "subprocess"])
def clients(request, docker_clients, subprocess_clients):
    if request.param == "docker":
        return docker_clients
    else:
        return subprocess_clients
