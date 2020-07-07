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

from substra.sdk.backends.local.hasher import Hasher


_BLOCK_SIZE = 64 * 1024


def hash_file(path):
    """Hash a file."""
    hasher = Hasher()

    with open(path, 'rb') as fp:
        while True:
            data = fp.read(_BLOCK_SIZE)
            if not data:
                break
            hasher.update(data)
    return hasher.compute()


def hash_directory(path, followlinks=False):
    """Hash a directory."""

    if not os.path.isdir(path):
        raise TypeError(f'{path} is not a directory.')

    hash_values = []
    for root, dirs, files in os.walk(path, topdown=True, followlinks=followlinks):
        dirs.sort()
        files.sort()

        for fname in files:
            hash_values.append(hash_file(os.path.join(root, fname)))

    return Hasher(values=sorted(hash_values)).compute()
