import contextlib
import copy
import functools
import io
import logging
import ntpath
import os
import re
import time
import uuid
import zipfile

from substra.sdk import exceptions
from substra.sdk import models


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


@contextlib.contextmanager
def extract_files(data, file_attributes):
    data = copy.deepcopy(data)

    paths = {}
    for attr in file_attributes:
        try:
            paths[attr] = data[attr]
        except KeyError:
            raise exceptions.LoadDataException(f"The '{attr}' attribute is missing.")
        del data[attr]

    files = {}
    for k, f in paths.items():
        if not os.path.exists(f):
            raise exceptions.LoadDataException(f"The '{k}' attribute file ({f}) does not exist.")
        files[k] = open(f, "rb")

    try:
        yield (data, files)
    finally:
        for f in files.values():
            f.close()


def zip_folder(fp, path):
    zipf = zipfile.ZipFile(fp, "w", zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(path):
        for f in files:
            abspath = os.path.join(root, f)
            archive_path = os.path.relpath(abspath, start=path)
            zipf.write(abspath, arcname=archive_path)
    zipf.close()


def zip_folder_in_memory(path):
    fp = io.BytesIO()
    zip_folder(fp, path)
    fp.seek(0)
    return fp


@contextlib.contextmanager
def extract_data_sample_files(data):
    # handle data sample specific case; paths and path cases
    data = copy.deepcopy(data)

    folders = {}
    if data.get("path"):
        attr = "path"
        folders[attr] = data[attr]
        del data[attr]

    if data.get("paths"):  # field is set and is not None/empty
        for p in data["paths"]:
            folders[path_leaf(p)] = p
        del data["paths"]

    files = {}
    for k, f in folders.items():
        if not os.path.isdir(f):
            raise exceptions.LoadDataException(f"Paths '{f}' is not an existing directory")
        files[k] = zip_folder_in_memory(f)

    try:
        yield (data, files)
    finally:
        for f in files.values():
            f.close()


def _check_metadata_search_filter(filter):
    if not isinstance(filter, dict):
        raise exceptions.FilterFormatError(
            "Cannot load filters. Please review the documentation, metadata filter should be a list of dict."
            "But one passed elements is not."
        )

    if "key" not in filter.keys() or "type" not in filter.keys():
        raise exceptions.FilterFormatError("Each metadata filter, must contains both `key` and `type` as key.")

    if filter["type"] not in ("is", "contains", "exists"):
        raise exceptions.FilterFormatError(
            "Each metadata filter `type` filed value must be `is`, `contains` or `exists`"
        )

    if filter["type"] in ("is", "contains"):
        if "value" not in filter.keys():
            raise exceptions.FilterFormatError(
                "For each metadata filter, if `type` value is `is` or `contains`, the filter should also contain the "
                "`value` key."
            )

        if not isinstance(filter.get("value"), str):
            raise exceptions.FilterFormatError(
                "For each metadata filter, if a `value` is passed, it should be a string."
            )


def _check_metadata_search_filters(filters):
    if not isinstance(filters, list):
        raise exceptions.FilterFormatError(
            "Cannot load filters. Please review the documentation, metadata filter should be a list of dict."
        )

    for filter in filters:
        _check_metadata_search_filter(filter)


def check_and_format_search_filters(asset_type, filters):  # noqa: C901
    # do not check if no filters
    if filters is None:
        return filters

    # check filters structure
    if not isinstance(filters, dict):
        raise exceptions.FilterFormatError(
            "Cannot load filters. Please review the documentation, filters should be a dict"
        )

    # retrieving asset allowed fields to filter on
    allowed_filters = models.SCHEMA_TO_MODEL[asset_type].allowed_filters()

    # for each attribute (key) to filter on
    for key in filters:
        # check that key is a valid filter
        if key not in allowed_filters:
            raise exceptions.NotAllowedFilterError(
                f"Cannot filter on {key}. Please review the documentation, filtering allowed only on {allowed_filters}"
            )
        elif key == "name":
            if not isinstance(filters[key], str):
                raise exceptions.FilterFormatError(
                    """Cannot load filters. Please review the documentation, 'name' filter is partial match in remote,
                    exact match in local, value should be str"""
                )
        elif key == "metadata":
            _check_metadata_search_filters(filters[key])

        # all other filters should be a list, throw an error if not
        elif not isinstance(filters[key], list):
            raise exceptions.FilterFormatError(
                "Cannot load filters. Please review the documentation, filters values should be a list"
            )
        # handle default case (List)
        else:
            # convert all keys to str, needed for rank as user can give int, can prevent errors if user doesn't give str
            filters[key] = [str(v) for v in filters[key]]

    return filters


def check_search_ordering(order_by):
    if order_by is None:
        return
    elif not models.OrderingFields.__contains__(order_by):
        raise exceptions.OrderingFormatError(
            f"Please review the documentation, ordering is available only on {list(models.OrderingFields.__members__)}"
        )


def retry_on_exception(exceptions, timeout=300):
    """Retry function in case of exception(s).

    Args:
        exceptions (list): list of exception types that trigger a retry
        timeout (int, optional): timeout in seconds

    Example:
        ```python
        from substra.sdk import exceptions, retry_on_exception

        def my_function(arg1, arg2):
            pass

        retry = retry_on_exception(
                    exceptions=(exceptions.RequestTimeout),
                    timeout=300,
                )
        retry(my_function)(arg1, arg2)
        ```
    """

    def _retry(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            delay = 1
            backoff = 2
            tstart = time.time()

            while True:
                try:
                    return f(*args, **kwargs)

                except exceptions:
                    if timeout is not False and time.time() - tstart > timeout:
                        raise
                    logging.warning(f"Function {f.__name__} failed: retrying in {delay}s")
                    time.sleep(delay)
                    delay *= backoff

        return wrapper

    return _retry


def response_get_destination_filename(response):
    """Get filename from content-disposition header."""
    disposition = response.headers.get("content-disposition")
    if not disposition:
        return None
    filenames = re.findall("filename=(.+)", disposition)
    if not filenames:
        return None
    filename = filenames[0]
    filename = filename.strip("'\"")
    return filename


def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
