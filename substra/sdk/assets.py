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

ALGO = 'algo'
DATA_SAMPLE = 'data_sample'
DATASET = 'dataset'
MODEL = 'model'
OBJECTIVE = 'objective'
TESTTUPLE = 'testtuple'
TRAINTUPLE = 'traintuple'
COMPUTE_PLAN = 'compute_plan'
NODE = 'node'

_SERVER_MAPPER = {
    DATASET: 'data_manager',
}


def get_all():
    return (
        ALGO,
        DATA_SAMPLE,
        DATASET,
        MODEL,
        OBJECTIVE,
        TESTTUPLE,
        TRAINTUPLE,
        COMPUTE_PLAN,
        NODE,
    )


def to_server_name(asset):
    try:
        return _SERVER_MAPPER[asset]
    except KeyError:
        return asset
