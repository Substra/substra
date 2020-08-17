import typing

from substra.sdk import exceptions, schemas


def _get_rank(node: str, visited: typing.Dict[str,
                                              int], edges: typing.Set[str],
              node_graph: typing.Dict[str, typing.List[str]]) -> int:
    if node in visited:
        return visited[node]
    for parent in node_graph[node]:
        edge = (node, parent)
        if edge in edges:
            raise exceptions.InvalidRequest(
                "missing dependency among inModels IDs", 400)
        else:
            edges.add(edge)

    if len(node_graph[node]) == 0:
        rank = 0
    else:
        rank = 1 + max([
            _get_rank(x, visited, edges, node_graph) for x in node_graph[node]
        ])
    visited[node] = rank
    return rank


def compute_ranks(
    node_graph: typing.Dict[str, typing.List[str]],
    visited: typing.Optional[typing.Dict[str, int]] = None
) -> typing.Dict[str, int]:
    """Compute the rank of the objects

    If visited is not empty, it should contain the id of the objects
    that already have a rank, these ids do not have to be in node_graph.

    Args:
        node_graph (typing.Dict[str, typing.List[str]]): List of tuple specifications
        whose rank is computed (read-only).
        visited (typing.Optional[typing.Dict[str, int]]): Dict id-rank of the
        tuple specifications whose rank has been computed (in place update).

    Raises:
        exceptions.InvalidRequest: if there is a circular dependency between the tuples.

    Returns:
        typing.Dict[str, int]: visited
            dict id - rank with all the ids from the node_graph
    """
    if visited is None:
        visited = dict()
    while len(visited) != len(node_graph):
        node = set(node_graph.keys()).difference(set(visited.keys())).pop()
        _get_rank(node=node,
                  visited=visited,
                  edges=set(),
                  node_graph=node_graph)
    return visited


def fill_tuple_lists(
    spec: schemas._BaseComputePlanSpec,
    tuple_graph: typing.Dict[str, typing.List[str]],
    traintuples: typing.Dict[str, schemas.ComputePlanTraintupleSpec],
    aggregatetuples: typing.Dict[str, schemas.ComputePlanAggregatetupleSpec],
    composite_traintuples: typing.Dict[
        str, schemas.ComputePlanCompositeTraintupleSpec],
    testtuples_by_train_id: typing.Dict[str, schemas.ComputePlanTesttupleSpec],
):
    """Update spec with the tuples in tuple_graph
    """
    for elem_id, _ in tuple_graph:
        if elem_id in traintuples:
            spec.traintuples.append(traintuples[elem_id])
        elif elem_id in aggregatetuples:
            spec.aggregatetuples.append(aggregatetuples[elem_id])
        elif elem_id in composite_traintuples:
            spec.composite_traintuples.append(composite_traintuples[elem_id])

        if elem_id in testtuples_by_train_id:
            spec.testtuples.append(testtuples_by_train_id[elem_id])
