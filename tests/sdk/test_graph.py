import pytest

from substra.sdk import exceptions
from substra.sdk import graph


@pytest.fixture
def node_graph():
    return {key: list(range(key)) for key in range(10)}


@pytest.fixture
def node_graph_linear():
    return {key: [key - 1] if key > 0 else list() for key in range(10)}


def test_compute_ranks(node_graph):
    visited = graph.compute_ranks(node_graph=node_graph)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_linear(node_graph_linear):
    visited = graph.compute_ranks(node_graph=node_graph_linear)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_no_correlation():
    node_graph = {key: list() for key in range(10)}
    visited = graph.compute_ranks(node_graph=node_graph)
    for _, rank in visited.items():
        assert rank == 0


def test_compute_ranks_cycle(node_graph):
    node_graph[5].append(9)
    with pytest.raises(exceptions.InvalidRequest) as e:
        graph.compute_ranks(node_graph=node_graph)

    assert "missing dependency among inModels IDs" in str(e.value)


def test_compute_ranks_closed_cycle(node_graph_linear):
    node_graph_linear[0] = [9]
    with pytest.raises(exceptions.InvalidRequest) as e:
        graph.compute_ranks(node_graph=node_graph_linear)

    assert "missing dependency among inModels IDs" in str(e.value)


def test_compute_ranks_ignore(node_graph):
    node_to_ignore = set(range(5))
    for i in range(5):
        node_graph.pop(i)
    visited = graph.compute_ranks(node_graph=node_graph, node_to_ignore=node_to_ignore)
    for key, rank in visited.items():
        assert rank == key - 5
