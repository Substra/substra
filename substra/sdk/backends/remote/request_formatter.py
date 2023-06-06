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
    if not ascending:
        return "-" + order_by
    return order_by
