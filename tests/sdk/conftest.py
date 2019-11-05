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

import substra


@pytest.fixture
def client(tmpdir):
    config_path = tmpdir / "substra.cfg"
    c = substra.Client(config_path=str(config_path))
    c.add_profile('test', 'foo', 'password', url="http://foo.io")
    return c


@pytest.fixture
def dataset_query(tmpdir):
    opener_path = tmpdir / "opener.py"
    opener_path.write_text("raise ValueError()", encoding="utf-8")

    desc_path = tmpdir / "description.md"
    desc_path.write_text("#Hello world", encoding="utf-8")

    return {
        "name": "dataset_name",
        "data_opener": str(opener_path),
        "type": "images",
        "description": str(desc_path),
        "objective_key": ""
    }


@pytest.fixture
def objective_query(tmpdir):
    metrics_path = tmpdir / "metrics.zip"
    metrics_path.write_text("foo archive", encoding="utf-8")

    desc_path = tmpdir / "description.md"
    desc_path.write_text("#Hello world", encoding="utf-8")

    return {
        "name": "metrics_name",
        "metrics": str(metrics_path),
        "description": str(desc_path),
        "test_data_keys": [],
        "test_data_sample_keys": []
    }


@pytest.fixture
def algo_query(tmpdir):
    algo_file_path = tmpdir / "algo.tar.gz"
    algo_file_path.write(b"tar gz archive")

    desc_path = tmpdir / "description.md"
    desc_path.write_text("#Hello world", encoding="utf-8")

    return {
        "name": "algo_name",
        "description": str(desc_path),
        "file": str(algo_file_path),
    }


@pytest.fixture
def data_sample_query(tmpdir):
    data_sample_dir_path = tmpdir / f"data_sample_0"
    data_sample_file_path = data_sample_dir_path / "data.txt"
    data_sample_file_path.write_text(f"Hello world 0", encoding="utf-8", ensure=True)

    return {
        "path": str(data_sample_dir_path),
        "data_manager_keys": ["42"],
    }


@pytest.fixture
def data_samples_query(tmpdir):
    nb = 3
    paths = []
    for i in range(nb):
        data_sample_dir_path = tmpdir / f"data_sample_{i}"
        data_sample_file_path = data_sample_dir_path / "data.txt"
        data_sample_file_path.write_text(
            f"Hello world {i}", encoding="utf-8", ensure=True)

        paths.append(str(data_sample_dir_path))

    return {
        "paths": paths,
        "data_manager_keys": ["42"],
    }
