import pytest

from substra.sdk import assets, exceptions


@pytest.fixture
def node_graph():
    return {
        key: list(range(key))
        for key in range(10)
    }


def test_compute_ranks(node_graph):
    visited = assets.compute_ranks(node_graph=node_graph)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_failure(node_graph):
    node_graph[5].append(9)
    with pytest.raises(exceptions.InvalidRequest):
        assets.compute_ranks(node_graph=node_graph)


def test_compute_ranks_update_visited(node_graph):
    visited = {
        key: key
        for key in range(5)
    }
    visited = assets.compute_ranks(node_graph=node_graph, visited=visited)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_update_visited_failure(node_graph):
    visited = {
        key: key
        for key in range(5)
    }
    node_graph[5].append(9)
    with pytest.raises(exceptions.InvalidRequest):
        visited = assets.compute_ranks(node_graph=node_graph, visited=visited)
