# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import typing
import sys

from substra.sdk import exceptions, schemas

sys.setrecursionlimit(15000)


def _get_rank(
    node: str,
    visited: typing.Dict[str, int],
    edges: typing.Set[str],
    node_graph: typing.Dict[str, typing.List[str]],
    node_to_ignore: typing.List[str],
) -> int:
    if node in visited:
        rank = visited[node]
    elif node in node_to_ignore:
        # Nodes to ignore have a rank of -1
        rank = -1
    else:
        for parent in node_graph[node]:
            edge = (node, parent)
            if edge in edges:
                raise exceptions.InvalidRequest(
                    "missing dependency among inModels IDs", 400
                )
            else:
                edges.add(edge)

        if len(node_graph[node]) == 0:
            rank = 0
        else:
            rank = 1 + max(
                [
                    _get_rank(x, visited, edges, node_graph, node_to_ignore)
                    for x in node_graph[node]
                ]
            )
    visited[node] = rank
    return rank


def compute_ranks(
    node_graph: typing.Dict[str, typing.List[str]],
    visited: typing.Optional[typing.Dict[str, int]] = None,
    node_to_ignore: typing.List[str] = None,
) -> typing.Dict[str, int]:
    """Compute the rank of the objects

    If visited is not empty, it should contain the id of the objects
    that already have a rank, these ids do not have to be in node_graph.

    Args:
        node_graph (typing.Dict[str, typing.List[str]]): List of tuple specifications
        whose rank is computed (read-only).
        visited (typing.Optional[typing.Dict[str, int]]): Dict id-rank of the
        tuple specifications whose rank has been computed (in place update).
        node_to_ignore (typing.List[str]): These nodes are ignored when encountered, a
        dependency on such a node is like no dependency

    Raises:
        exceptions.InvalidRequest: if there is a circular dependency between the tuples.

    Returns:
        typing.Dict[str, int]: visited
            dict id - rank with all the ids from the node_graph
    """
    if visited is None:
        visited = dict()
    if node_to_ignore is None:
        node_to_ignore = list()
    while len(visited) != len(node_graph):
        node = set(node_graph.keys()).difference(set(visited.keys())).pop()
        _get_rank(
            node=node,
            visited=visited,
            edges=set(),
            node_graph=node_graph,
            node_to_ignore=node_to_ignore,
        )
    return visited


def filter_tuples_in_list(
    tuple_graph: typing.Dict[str, typing.List[str]],
    traintuples: typing.Dict[str, schemas.ComputePlanTraintupleSpec],
    aggregatetuples: typing.Dict[str, schemas.ComputePlanAggregatetupleSpec],
    composite_traintuples: typing.Dict[str, schemas.ComputePlanCompositeTraintupleSpec],
    testtuples: typing.Dict[str, schemas.ComputePlanTesttupleSpec],
):
    """Return the tuple lists with only the elements which are in the tuple graph.
    """
    filtered_traintuples = list()
    filtered_aggregatetuples = list()
    filtered_composite_traintuples = list()
    filtered_testtuples = list()
    for elem_id, _ in tuple_graph:
        if elem_id in traintuples:
            filtered_traintuples.append(traintuples[elem_id])
        elif elem_id in aggregatetuples:
            filtered_aggregatetuples.append(aggregatetuples[elem_id])
        elif elem_id in composite_traintuples:
            filtered_composite_traintuples.append(composite_traintuples[elem_id])
        elif elem_id in testtuples:
            filtered_testtuples.append(testtuples[elem_id])

    return (
        filtered_traintuples,
        filtered_aggregatetuples,
        filtered_composite_traintuples,
        filtered_testtuples,
    )
