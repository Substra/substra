import contextlib
import copy
import io
import itertools
import functools
import json
import logging
import time
import os
import re
from urllib.parse import quote
import zipfile

import ntpath


class LoadDataException(Exception):
    pass


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
            raise LoadDataException(f"The '{attr}' attribute is missing.")
        del data[attr]

    files = {}
    for k, f in paths.items():
        if not os.path.exists(f):
            raise LoadDataException(f"The '{k}' attribute file ({f}) does not exit.")
        files[k] = open(f, 'rb')

    try:
        yield (data, files)
    finally:
        for f in files.values():
            f.close()


def zip_folder(fp, path):
    zipf = zipfile.ZipFile(fp, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
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
    if data.get('path'):
        attr = 'path'
        folders[attr] = data[attr]
        del data[attr]

    for p in list(data.get('paths', [])):
        folders[path_leaf(p)] = p
        data['paths'].remove(p)

    files = {}
    for k, f in folders.items():
        if not os.path.isdir(f):
            raise LoadDataException(f"Paths '{f}' is not an existing directory")
        files[k] = zip_folder_in_memory(f)

    try:
        yield (data, files)
    finally:
        for f in files.values():
            f.close()


def flatten(list_of_list):
    res = []
    for item in itertools.chain.from_iterable(list_of_list):
        if item not in res:
            res.append(item)
    return res


def parse_filters(filters):
    try:
        filters = json.loads(filters)
    except ValueError:
        raise ValueError(
            'Cannot load filters. Please review the documentation.')

    def _escape_filter(f):
        # handle OR
        if f == 'OR':
            return '-OR-'

        # handle filter value that contains ":"
        try:
            asset, field, *value = f.split(':')
        except ValueError:
            return f

        return ':'.join([asset, field, quote(quote(':'.join(value)))])

    filters = map(_escape_filter, filters)

    # requests uses quote_plus to escape the params, but we want to use
    # quote
    # we're therefore passing a string (won't be escaped again) instead
    # of an object
    return 'search=%s' % quote(''.join(filters))


def retry_on_exception(exceptions, timeout=False):
    """Retry function in case of exception(s)."""
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
                    logging.warning(
                        f'Function {f.__name__} failed: retrying in {delay}s')
                    time.sleep(delay)
                    delay *= backoff

        return wrapper
    return _retry


def response_get_destination_filename(response):
    """Get filename from content-disposition header."""
    disposition = response.headers.get('content-disposition')
    if not disposition:
        return None
    filenames = re.findall("filename=(.+)", disposition)
    if not filenames:
        return None
    filename = filenames[0]
    filename = filename.strip('\'"')
    return filename
