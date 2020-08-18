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

import pytest

from substra.sdk import graph, exceptions


@pytest.fixture
def node_graph():
    return {
        key: list(range(key))
        for key in range(10)
    }


def test_compute_ranks(node_graph):
    visited = graph.compute_ranks(node_graph=node_graph)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_failure(node_graph):
    node_graph[5].append(9)
    with pytest.raises(exceptions.InvalidRequest) as e:
        graph.compute_ranks(node_graph=node_graph)

    assert 'missing dependency among inModels IDs' in str(e.value)


def test_compute_ranks_update_visited(node_graph):
    visited = {
        key: key
        for key in range(5)
    }
    visited = graph.compute_ranks(node_graph=node_graph, visited=visited)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_update_visited_failure(node_graph):
    visited = {
        key: key
        for key in range(5)
    }
    node_graph[5].append(9)
    with pytest.raises(exceptions.InvalidRequest) as e:
        visited = graph.compute_ranks(node_graph=node_graph, visited=visited)

    assert 'missing dependency among inModels IDs' in str(e.value)
