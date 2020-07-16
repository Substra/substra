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

from substra.sdk import exceptions


def __get_rank(
        node: str,
        visited: typing.Dict[str, int],
        edges: typing.Set[str],
        node_graph: typing.Dict[str, typing.List[str]]
        ) -> int:
    if node in visited:
        return visited[node]
    for parent in node_graph[node]:
        edge = (node, parent)
        if edge in edges:
            raise exceptions.InvalidRequest("missing dependency among inModels IDs", 400)
        else:
            edges.add(edge)

    if len(node_graph[node]) == 0:
        rank = 0
    else:
        rank = 1 + max([
            __get_rank(x, visited, edges, node_graph)
            for x in node_graph[node]
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
        __get_rank(
            node=node,
            visited=visited,
            edges=set(),
            node_graph=node_graph
        )
    return visited
