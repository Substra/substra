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


def format_search_filters_for_remote(filters):
    formatted_filters = {}
    # do not process if no filters
    if filters is None:
        return formatted_filters

    for key in filters:
        # handle special cases name and metadata
        if key == "name":
            formatted_filters["match"] = filters[key]
        elif key == "metadata":
            formatted_filters["metadata"] = json.dumps(filters["metadata"]).replace(" ", "")

        else:
            # all other filters are formatted as a csv string without spaces
            values = ",".join(filters[key])
            formatted_filters[key] = values.replace(" ", "")

    return formatted_filters


def format_search_ordering_for_remote(order_by, ascending):
    if ascending:
        return "-" + order_by
    return order_by
