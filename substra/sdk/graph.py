import typing

from substra.sdk import exceptions


def _get_inverted_node_graph(node_graph, node_to_ignore):
    """Get the graph {node_id: nodes that depend on this one}
    Also this graph does not contain the nodes to ignore
    """
    inverted = dict()
    for node, dependencies in node_graph.items():
        if node not in node_to_ignore:
            for dependency in dependencies:
                if dependency not in node_to_ignore:
                    inverted.setdefault(dependency, list())
                    inverted[dependency].append(node)
    return inverted


def _get_current_node(visited, ranks):
    """Find the next node to visit: node with the minimum rank not yet visited."""
    current_node = None
    current_rank = None
    for node, rank in ranks.items():
        if node not in visited and (current_rank is None or rank < current_rank):
            current_node = node
            current_rank = rank
    # Failure means that there is a closed cycle: A -> B -> ... -> A
    if current_node is None:
        raise exceptions.InvalidRequest("missing dependency among inModels IDs", 400)
    return current_node


def compute_ranks(
    node_graph: typing.Dict[str, typing.List[str]],
    node_to_ignore: typing.Set[str] = None,
    ranks: typing.Dict[str, int] = None,
) -> typing.Dict[str, int]:
    """Compute the ranks of the nodes in the graph.

    Args:
        node_graph (typing.Dict[str, typing.List[str]]):
            Dict {node_id: list of nodes it depends on}.
            Node graph keys must not contain any node to ignore.
        node_to_ignore (typing.Set[str], optional): List of nodes to ignore.
            Defaults to None.
        ranks (typing.Dict[str, int]): Already computed ranks. Defaults to None.

    Raises:
        exceptions.InvalidRequest: If the node graph contains a cycle

    Returns:
        typing.Dict[str, int]: Dict { node_id : rank }
    """
    ranks = ranks or dict()
    visited = set()
    node_to_ignore = node_to_ignore or set()

    extra_nodes = set(node_graph.keys()).intersection(node_to_ignore)
    if len(extra_nodes) > 0:
        raise ValueError(f"node_graph keys should not contain any node to ignore: {extra_nodes}")

    inverted_node_graph = _get_inverted_node_graph(node_graph, node_to_ignore)

    # Assign rank 0 to nodes without deps
    for node, dependencies in node_graph.items():
        if node not in node_to_ignore:
            actual_deps = [dep for dep in dependencies if dep not in node_to_ignore]
            if len(actual_deps) == 0:
                ranks[node] = 0

    edges = set()

    while len(visited) != len(node_graph):
        current_node = _get_current_node(visited, ranks)
        visited.add(current_node)
        for child in inverted_node_graph.get(current_node, list()):
            ranks[child] = max(ranks[current_node] + 1, ranks.get(child, -1))

            # Cycle detection
            edge = (current_node, child)
            if (edge[1], edge[0]) in edges:
                raise exceptions.InvalidRequest(
                    f"missing dependency among inModels IDs, \
                        circular dependency between {edge[0]} and {edge[1]}",
                    400,
                )
            else:
                edges.add(edge)

    return ranks
