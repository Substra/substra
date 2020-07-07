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


from substra.sdk.backends.remote.backend import Remote
from substra.sdk.backends.local.backend import Local


_BACKEND_CHOICES = {
    'remote': Remote,
    'local': Local,
}


def get(name, *args, **kwargs):
    return _BACKEND_CHOICES[name.lower()](*args, **kwargs)
