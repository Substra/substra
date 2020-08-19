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

from substra.sdk import exceptions, schemas


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
) -> typing.Dict[str, int]:

    node_to_ignore = node_to_ignore or set()
    inverted_node_graph = _get_inverted_node_graph(node_graph, node_to_ignore)

    # Number of nodes to visit
    n_nodes = len(set(node_graph.keys()).difference(node_to_ignore))

    # Assign rank 0 to nodes without deps
    ranks = dict()
    for node, dependencies in node_graph.items():
        if node not in node_to_ignore:
            actual_deps = [dep for dep in dependencies if dep not in node_to_ignore]
            if len(actual_deps) == 0:
                ranks[node] = 0

    visited = set()
    edges = set()

    while len(visited) != n_nodes:
        current_node = _get_current_node(visited, ranks)
        visited.add(current_node)
        for child in inverted_node_graph.get(current_node, list()):
            ranks[child] = max(ranks[current_node] + 1, ranks.get(child, -1))

            # Cycle detection
            edge = (current_node, child)
            if edge in edges or (edge[1], edge[0]) in edges:
                raise exceptions.InvalidRequest(
                    "missing dependency among inModels IDs", 400
                )
            else:
                edges.add(edge)

    return ranks


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
