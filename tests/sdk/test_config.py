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

from substra.sdk.config import ConfigManager, ProfileNotFoundError, ConfigException


def test_init_non_existing_paths(tmpdir):
    config_path = tmpdir / 'non_existing_config_path.json'
    tokens_path = tmpdir / 'non_existing_tokens_path.json'
    assert not os.path.exists(config_path)
    assert not os.path.exists(tokens_path)
    ConfigManager(config_path, tokens_path)
    assert not os.path.exists(config_path)
    assert not os.path.exists(tokens_path)


def test_init_non_existing_tokens_path(tmpdir):
    config_path = tmpdir / 'config.json'
    tokens_path = tmpdir / 'non_existing_tokens_path.json'
    config_path.write_text(json.dumps({'tokens_path': str(tokens_path)}), 'utf-8')

    assert not os.path.exists(tokens_path)
    ConfigManager(config_path)
    assert not os.path.exists(tokens_path)


def test_init_invalid_config_path_content(tmpdir):
    config_path = tmpdir / 'invalid_content.json'
    config_path.write_text('definitely not json', 'utf-8')
    with pytest.raises(ConfigException, match='Cannot parse config file'):
        ConfigManager(config_path)


def test_init_invalid_tokens_path_content(tmpdir):
    config_path = tmpdir / 'config.json'
    tokens_path = tmpdir / 'invalid_content.json'
    tokens_path.write_text('definitely not json', 'utf-8')
    with pytest.raises(ConfigException, match='Cannot parse tokens file'):
        ConfigManager(config_path, tokens_path)


def test_init_valid_path_content(tmpdir):
    profiles = {'foo': 'bar'}
    config_path = tmpdir / 'config.json'
    config_path.write_text(json.dumps({'profiles': profiles}), 'utf-8')

    config_manager = ConfigManager(config_path)
    assert config_manager._profiles == profiles


def test_get_existing_profile(tmpdir):
    config_path = tmpdir / 'config.json'
    config_path.write_text(json.dumps({
        'profiles': {
            'foo': {
                'url': 'http://foo.example.com',
            }
        }
    }), 'utf-8')
    config_manager = ConfigManager(config_path)

    assert config_manager.get_profile('foo') == {
        'url': 'http://foo.example.com',
    }


def test_get_non_existing_profile():
    config_manager = ConfigManager()
    with pytest.raises(ProfileNotFoundError):
        config_manager.get_profile('foo')


def test_set_new_profile():
    profile = {'url': 'http://foo.example.com', 'version': '0.0', 'insecure': False}
    config_manager = ConfigManager()
    config_manager.set_profile('foo', 'http://foo.example.com')
    assert config_manager.get_profile('foo') == profile

    config_manager.set_token('foo', 'foo token')
    profile.update({'token': 'foo token'})
    assert config_manager.get_profile('foo') == profile


def test_set_existing_profile():
    config_manager = ConfigManager()
    original_profile = {'url': 'foo', 'version': '0.0', 'insecure': False, 'token': 'foo'}
    new_profile = {'url': 'bar', 'version': '0.0', 'insecure': False, 'token': 'bar'}

    config_manager.set_profile('foo', **original_profile)
    assert config_manager.get_profile('foo') == original_profile
    config_manager.set_profile('foo', **new_profile)
    assert config_manager.get_profile('foo') == new_profile


def test_save_profiles(tmpdir):
    config_path = str(tmpdir / 'config.json')
    tokens_path = str(tmpdir / 'tokens.json')
    assert not os.path.exists(config_path)
    assert not os.path.exists(tokens_path)
    config_manager = ConfigManager(config_path, tokens_path)
    config_manager.set_profile('foo', url='foo', token='foo')
    config_manager.save()

    with open(config_path, 'r') as f:
        assert json.load(f) == {
            'tokens_path': tokens_path,
            'profiles': {
                'foo': {
                    'url': 'foo',
                    'version': '0.0',
                    'insecure': False,
                },
            },
        }

    with open(tokens_path, 'r') as f:
        assert json.load(f) == {
            'foo': 'foo',
        }
