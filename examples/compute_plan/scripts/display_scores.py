import json
import math
import os

import substra

current_directory = os.path.dirname(__file__)
compute_plan_keys_path = os.path.join(current_directory, '../compute_plan_keys.json')

client = substra.Client(os.path.join(current_directory, '../../config.json'), 'owkin')

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
    columns[2].append(testtuple['model']['traintupleKey'])
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


