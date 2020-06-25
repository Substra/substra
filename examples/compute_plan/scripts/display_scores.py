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
import math
import os

import substra

current_directory = os.path.dirname(__file__)
compute_plan_keys_path = os.path.join(current_directory, '../compute_plan_keys.json')

client = substra.Client(profile_name="node-1")

with open(compute_plan_keys_path, 'r') as f:
    compute_plan_keys = json.load(f)

# fetch all data
testtuple_keys = compute_plan_keys['testtupleKeys']
columns = [
    ['STEP'],
    ['SCORE'],
    ['TRAINTUPLE'],
    ['TESTTUPLE'],
]
for i, testtuple_key in enumerate(testtuple_keys):
    testtuple = client.get_testtuple(testtuple_key)
    score = testtuple['dataset']['perf'] if testtuple['status'] == 'done' else testtuple['status']
    columns[0].append(str(i+1))
    columns[1].append(str(score))
    columns[2].append(testtuple['traintupleKey'])
    columns[3].append(testtuple['key'])

# display data
column_widths = []
for column in columns:
    width = max([len(x) for x in column])
    width = (math.ceil(width / 4) + 1) * 4
    column_widths.append(width)

for row_index in range(len(testtuple_keys) + 1):
    for col_index, column in enumerate(columns):
        print(column[row_index].ljust(column_widths[col_index]), end='')
    print()
