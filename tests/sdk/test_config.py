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
import json

import pytest

import substra
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


def test_add_load_profile_from_file(tmpdir):
    path = tmpdir / 'substra.cfg'
    conf = {
       "node-1": {
           "auth": {
               "username": "node-1"
           },
           "insecure": False,
           "url": "http://substra-backend.node-1.com",
           "version": "0.0"
       },
    }

    path.write_text(json.dumps(conf), "UTF-8")
    manager = configuration.Manager(str(path))
    profile = manager.load_profile('node-1')

    assert conf['node-1'] == profile


def test_add_load_bad_profile_from_file(tmpdir):
    path = tmpdir / 'substra.cfg'
    conf = "node-1"

    path.write_text(conf, "UTF-8")
    manager = configuration.Manager(str(path))

    with pytest.raises(configuration.ConfigException):
        manager.load_profile('node-1')


def test_load_profile_fail(tmpdir):
    path = tmpdir / 'substra.cfg'
    manager = configuration.Manager(str(path))

    with pytest.raises(configuration.ConfigException):
        manager.load_profile('notfound')

    manager.add_profile('default', 'foo', 'bar')

    with pytest.raises(configuration.ProfileNotFoundError):
        manager.load_profile('notfound')


def test_login_without_profile(tmpdir):
    client = substra.Client()

    with pytest.raises(substra.exceptions.SDKException):
        client.login()
