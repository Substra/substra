import tarfile
import zipfile

from substra.sdk import exceptions
from substra.sdk.archive import tarsafe
from substra.sdk.archive.safezip import ZipFile


def _untar(archive, to_):
    with tarsafe.open(archive, "r:*") as tf:
        tf.extractall(to_)


def _unzip(archive, to_):
    with ZipFile(archive, "r") as zf:
        zf.extractall(to_)


def uncompress(archive, to_):
    """Uncompress tar or zip archive to destination."""
    if tarfile.is_tarfile(archive):
        _untar(archive, to_)
    elif zipfile.is_zipfile(archive):
        _unzip(archive, to_)
    else:
        raise exceptions.InvalidRequest(f"Cannot uncompress '{archive}'", 400)
