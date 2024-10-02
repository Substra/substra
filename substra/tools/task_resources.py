import json
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from substratools import exceptions


class StaticInputIdentifiers(str, Enum):
    opener = "opener"
    datasamples = "datasamples"
    chainkeys = "chainkeys"
    rank = "rank"


_RESOURCE_ID = "id"
_RESOURCE_VALUE = "value"
_RESOURCE_MULTIPLE = "multiple"


def _check_resources_format(resource_list):

    _required_keys = set((_RESOURCE_ID, _RESOURCE_VALUE, _RESOURCE_MULTIPLE))
    _error_message = (
        "`--inputs` and `--outputs` args should be json serialized list of dict. Each dict containing "
        f"the following keys: {_required_keys}. {_RESOURCE_ID} and {_RESOURCE_VALUE} must be strings, "
        f"{_RESOURCE_MULTIPLE} must be a bool."
    )

    if not isinstance(resource_list, list):
        raise exceptions.InvalidCLIError(_error_message)

    if not all([isinstance(d, dict) for d in resource_list]):
        raise exceptions.InvalidCLIError(_error_message)

    if not all([set(d.keys()) == _required_keys for d in resource_list]):
        raise exceptions.InvalidCLIError(_error_message)

    if not all([isinstance(d[_RESOURCE_MULTIPLE], bool) for d in resource_list]):
        raise exceptions.InvalidCLIError(_error_message)

    if not all([isinstance(d[_RESOURCE_ID], str) for d in resource_list]):
        raise exceptions.InvalidCLIError(_error_message)

    if not all([isinstance(d[_RESOURCE_VALUE], str) for d in resource_list]):
        raise exceptions.InvalidCLIError(_error_message)


def _check_resources_multiplicity(resource_dict):
    for k, v in resource_dict.items():
        if not v[_RESOURCE_MULTIPLE] and len(v[_RESOURCE_VALUE]) > 1:
            raise exceptions.InvalidInputOutputsError(f"There is more than one path for the non multiple resource {k}")


class TaskResources:
    """TaskResources is created from stdin to provide a nice abstraction over inputs/outputs"""

    _values: Dict[str, List[str]]

    def __init__(self, argstr: str) -> None:
        """Argstr is expected to be a JSON array like:
        [
            {"id": "local", "value": "/sandbox/output/model/uuid", "multiple": False},
            {"id": "shared", ...}
        ]
        """
        self._values = {}
        resource_list = json.loads(argstr.replace("\\", "/"))

        _check_resources_format(resource_list)

        for item in resource_list:
            self._values.setdefault(
                item[_RESOURCE_ID], {_RESOURCE_VALUE: [], _RESOURCE_MULTIPLE: item[_RESOURCE_MULTIPLE]}
            )
            self._values[item[_RESOURCE_ID]][_RESOURCE_VALUE].append(item[_RESOURCE_VALUE])

        _check_resources_multiplicity(self._values)

        self.opener_path = self.get_value(StaticInputIdentifiers.opener.value)
        self.input_data_folder_paths = self.get_value(StaticInputIdentifiers.datasamples.value)
        self.chainkeys_path = self.get_value(StaticInputIdentifiers.chainkeys.value)

    def get_value(self, key: str) -> Optional[Union[List[str], str]]:
        """Returns the value for a given key. Return None if there is no matching resource.
        Will raise if there is a mismatch between the given multiplicity and the number of returned
        elements.

        If multiple is True, will return a list else will return a single value
        """
        if key not in self._values:
            return None

        val = self._values[key][_RESOURCE_VALUE]
        multiple = self._values[key][_RESOURCE_MULTIPLE]

        if multiple:
            return val

        return val[0]

    @property
    def formatted_dynamic_resources(self) -> Union[List[str], str]:
        """Returns all the resources (except the datasamples, the opener and the chainkeys_path under the user format:
        A dict where each input is an element where
            - the key is the user identifier
            - the value is a list of Path for multiple resources and a Path for non multiple resources
        """

        return {
            k: self.get_value(k)
            for k in self._values.keys()
            if k
            not in (
                StaticInputIdentifiers.opener.value,
                StaticInputIdentifiers.datasamples.value,
                StaticInputIdentifiers.chainkeys.value,
            )
        }
