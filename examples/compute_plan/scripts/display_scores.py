import json
import math
import os

import substra

current_directory = os.path.dirname(__file__)
compute_plan_info_path = os.path.join(current_directory, "../compute_plan_info.json")

client = substra.Client.from_config_file(profile_name="organization-1")

with open(compute_plan_info_path, "r") as f:
    compute_plan_info = json.load(f)

# fetch all data
testtuples = client.list_testtuple(filters={"compute_plan_key": [compute_plan_info["key"]]})
columns = [
    ["STEP"],
    ["SCORE"],
    ["TRAINTUPLE"],
    ["TESTTUPLE"],
]
testtuples = sorted(testtuples, key=lambda x: x.rank)

for testtuple in testtuples:
    if testtuple.status == "STATUS_DONE":
        score = list(testtuple.test.perfs.values())[0]
    else:
        score = testtuple.status

    columns[0].append(str(testtuple.rank + 1))
    columns[1].append(str(score))
    columns[2].append(testtuple.parent_task_keys[0])
    columns[3].append(testtuple.key)

# display data
column_widths = []
for column in columns:
    width = max([len(x) for x in column])
    width = (math.ceil(width / 4) + 1) * 4
    column_widths.append(width)

for row_index in range(len(testtuples) + 1):
    for col_index, column in enumerate(columns):
        print(column[row_index].ljust(column_widths[col_index]), end="")
    print()
