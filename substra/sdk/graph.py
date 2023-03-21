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
                    inverted.setdefault(dependency, [])
                    inverted[dependency].append(node)
    return inverted


def _breadth_first_traversal_rank(
    ranks: typing.Dict[str, int], inverted_node_graph: typing.Dict[str, typing.List[str]]
):
    edges = set()
    queue = [node for node in ranks]
    visited = set(queue)

    if len(queue) == 0:
        raise exceptions.InvalidRequest("missing dependency among inModels IDs, circular dependency found", 400)

    while len(queue) > 0:
        current_node = queue.pop(0)
        for child in inverted_node_graph.get(current_node, []):
            new_child_rank = max(ranks[current_node] + 1, ranks.get(child, -1))

            if new_child_rank != ranks.get(child, -1):
                # either the child has never been visited
                # or its rank has been updated and we must visit again
                ranks[child] = new_child_rank
                visited.add(child)
                queue.append(child)

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
    node_to_ignore = node_to_ignore or set()

    if len(node_graph) == 0:
        return dict()

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

    ranks = _breadth_first_traversal_rank(ranks=ranks, inverted_node_graph=inverted_node_graph)

    return ranks
