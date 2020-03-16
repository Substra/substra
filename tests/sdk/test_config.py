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
import os

import pytest

from substra.sdk.config import ProfileConfigManager, ProfileTokenManager, ProfileNotFoundError, \
    ConfigException


@pytest.mark.parametrize('profile_manager_cls', (ProfileConfigManager, ProfileTokenManager))
def test_init_non_existing_path(tmpdir, profile_manager_cls):
    path = tmpdir / 'non_existing_path.json'
    assert not os.path.exists(path)
    profile_manager_cls(path)
    assert not os.path.exists(path)


@pytest.mark.parametrize('profile_manager_cls', (ProfileConfigManager, ProfileTokenManager))
def test_init_invalid_path_content(tmpdir, profile_manager_cls):
    path = tmpdir / 'invalid_content.json'
    path.write_text('definitely not json', 'utf-8')
    with pytest.raises(ConfigException, match='Cannot parse config file'):
        profile_manager_cls(path)


@pytest.mark.parametrize('profile_manager_cls', (ProfileConfigManager, ProfileTokenManager))
def test_init_valid_path_content(tmpdir, profile_manager_cls):
    profiles = {'foo': 'bar'}
    path = tmpdir / 'valid_content.json'
    path.write_text(json.dumps(profiles), 'utf-8')

    profile_manager = profile_manager_cls(path)
    assert profile_manager.profiles == profiles


@pytest.mark.parametrize('profile_manager_cls', (ProfileConfigManager, ProfileTokenManager))
def test_override_profiles(tmpdir, profile_manager_cls):
    path_profiles = {'foo': {}}
    profiles_override = {'bar': {}}
    path = tmpdir / 'valid_content.json'
    path.write_text(json.dumps(path_profiles), 'utf-8')

    profile_manager = profile_manager_cls(path=path, profiles=profiles_override)
    assert profile_manager.profiles == profiles_override


@pytest.mark.parametrize('profile_manager_cls', (ProfileConfigManager, ProfileTokenManager))
def test_get_existing_profile(profile_manager_cls):
    profiles = {'foo': 'bar'}
    profile_manager = profile_manager_cls(profiles=profiles)
    assert profile_manager.get_profile('foo') == 'bar'


@pytest.mark.parametrize('profile_manager_cls', (ProfileConfigManager, ProfileTokenManager))
def test_get_non_existing_profile(profile_manager_cls):
    profile_manager = profile_manager_cls()
    with pytest.raises(ProfileNotFoundError):
        profile_manager.get_profile('foo')


@pytest.mark.parametrize('profile_manager_cls,profile', (
    (ProfileConfigManager, {'url': 'foo', 'version': '0.0', 'insecure': False}),
    (ProfileTokenManager, {'token': 'foo'}),
))
def test_set_new_profile(profile_manager_cls, profile):
    profile_manager = profile_manager_cls()
    profile_manager.set_profile('foo', **profile)
    assert profile_manager.get_profile('foo') == profile


@pytest.mark.parametrize('profile_manager_cls,existing_profile,new_profile', (
    (
        ProfileConfigManager,
        {'url': 'foo', 'version': '0.0', 'insecure': False},
        {'url': 'bar', 'version': '0.0', 'insecure': False},
    ),
    (
        ProfileTokenManager,
        {'token': 'foo'},
        {'token': 'bar'},
    ),
))
def test_set_existing_profile(profile_manager_cls, existing_profile, new_profile):
    profile_manager = profile_manager_cls(profiles={'foo': existing_profile})
    assert profile_manager.get_profile('foo') == existing_profile
    profile_manager.set_profile('foo', **new_profile)
    assert profile_manager.get_profile('foo') == new_profile


@pytest.mark.parametrize('profile_manager_cls,profiles', (
    (ProfileConfigManager, {'foo': {'url': 'foo', 'version': '0.0', 'insecure': False}}),
    (ProfileTokenManager, {'foo': {'token': 'foo'}}),
))
def test_save_profiles(tmpdir, profile_manager_cls, profiles):
    path = tmpdir / 'profiles.json'
    assert not os.path.exists(path)
    profile_manager = profile_manager_cls(path, profiles)
    profile_manager.save_profiles()
    with open(path, 'r') as f:
        assert json.load(f) == profiles
