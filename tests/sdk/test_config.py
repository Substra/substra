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

import substra.sdk.config as configuration


def test_add_load_profile(tmpdir):
    path = tmpdir / 'substra.cfg'
    manager = configuration.Manager(str(path))

    profile_1 = manager.add_profile(
        'owkin',
        'substra',
        'p@$swr0d44',
        url='http://substra-backend.owkin.xyz:8000',
        version='0.0')

    profile_2 = manager.load_profile('owkin')
    assert profile_1 == profile_2


def test_load_profile_fail(tmpdir):
    path = tmpdir / 'substra.cfg'
    manager = configuration.Manager(str(path))

    with pytest.raises(FileNotFoundError):
        manager.load_profile('notfound')

    manager.add_profile('default', 'foo', 'bar')

    with pytest.raises(configuration.ProfileNotFoundError):
        manager.load_profile('notfound')
