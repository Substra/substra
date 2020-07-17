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

import os
import zipfile

import pytest

from substra.sdk import utils, exceptions


def _unzip(fp, destination):
    with zipfile.ZipFile(fp, 'r') as zipf:
        zipf.extractall(destination)


def test_zip_folder(tmp_path):
    # initialise dir to zip
    dir_to_zip = tmp_path / "dir"
    dir_to_zip.mkdir()

    file_items = [
        ("name0.txt", "content0"),
        ("dir1/name1.txt", "content1"),
        ("dir2/name2.txt", "content2"),
    ]

    for name, content in file_items:
        path = dir_to_zip / name
        path.parents[0].mkdir(exist_ok=True)
        path.write_text(content)

    for name, _ in file_items:
        path = dir_to_zip / name
        assert os.path.exists(str(path))

    # zip dir
    fp = utils.zip_folder_in_memory(str(dir_to_zip))
    assert fp

    # unzip dir
    destination_dir = tmp_path / "destination"
    destination_dir.mkdir()
    _unzip(fp, str(destination_dir))
    for name, content in file_items:
        path = destination_dir / name
        assert os.path.exists(str(path))
        assert path.read_text() == content


@pytest.mark.parametrize('raw, parsed', [
    (['foo'], ['foo']),
    (['foo', 'bar'], ['foo,bar']),
    (['foo', '-OR-', 'bar'], ['foo', '-OR-', 'bar']),
    (['foo', 'bar', '-OR-', 'baz'], ['foo,bar', '-OR-', 'baz']),
    (['foo', 'bar', '-OR-', 'baz', 'qux'], ['foo,bar', '-OR-', 'baz,qux']),
    (['foo', '-OR-', 'bar', 'baz', 'qux'], ['foo', '-OR-', 'bar,baz,qux']),
    (['foo', '-OR-', 'bar', '-OR-', 'baz'], ['foo', '-OR-', 'bar', '-OR-', 'baz']),
    (['foo', 'bar', '-OR-', 'baz', 'qux', '-OR-', 'quux', 'corge'],
     ['foo,bar', '-OR-', 'baz,qux', '-OR-', 'quux,corge']),
])
def test_join_and_groups(raw, parsed):
    assert utils._join_and_groups(raw) == parsed


@pytest.mark.parametrize('raw,parsed,exception', [
    (["foo", "OR", "bar"], 'search=foo-OR-bar', None),
    (["foo:bar:baz"], 'search=foo%3Abar%3Abaz', None),
    (["foo:bar:baz qux"], 'search=foo%3Abar%3Abaz%252520qux', None),
    (["foo:bar:baz:qux"], 'search=foo%3Abar%3Abaz%25253Aqux', None),
    (["foo", "bar"], 'search=foo%2Cbar', None),
    (None, None, ValueError),
    ('foo', None, ValueError),
    ({}, None, ValueError),
])
def test_parse_filters(raw, parsed, exception):
    if exception:
        with pytest.raises(exception):
            utils.parse_filters(raw)
    else:
        assert utils.parse_filters(raw) == parsed


@pytest.fixture
def node_graph():
    return {
        key: list(range(key))
        for key in range(10)
    }


def test_compute_ranks(node_graph):
    visited = utils.compute_ranks(node_graph=node_graph)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_failure(node_graph):
    node_graph[5].append(9)
    with pytest.raises(exceptions.InvalidRequest) as e:
        utils.compute_ranks(node_graph=node_graph)

    assert 'missing dependency among inModels IDs' in str(e.value)


def test_compute_ranks_update_visited(node_graph):
    visited = {
        key: key
        for key in range(5)
    }
    visited = utils.compute_ranks(node_graph=node_graph, visited=visited)
    for key, rank in visited.items():
        assert key == rank


def test_compute_ranks_update_visited_failure(node_graph):
    visited = {
        key: key
        for key in range(5)
    }
    node_graph[5].append(9)
    with pytest.raises(exceptions.InvalidRequest) as e:
        visited = utils.compute_ranks(node_graph=node_graph, visited=visited)

    assert 'missing dependency among inModels IDs' in str(e.value)
