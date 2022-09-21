import pytest

import substra


@pytest.fixture(scope="session")
def docker_clients():
    return [substra.Client(backend_type=substra.BackendType.LOCAL_DOCKER) for _ in range(2)]


@pytest.fixture(scope="session")
def subprocess_clients():
    return [substra.Client(backend_type=substra.BackendType.LOCAL_SUBPROCESS) for _ in range(2)]


@pytest.fixture(scope="session", params=["docker", "subprocess"])
def clients(request, docker_clients, subprocess_clients):
    if request.param == "docker":
        return docker_clients
    else:
        return subprocess_clients
