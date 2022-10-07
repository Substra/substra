import tarfile
import zipfile

from substra.sdk import exceptions
from substra.sdk.archive import tarsafe
from substra.sdk.archive.safezip import ZipFile


def _untar(archive, to_):
    with tarsafe.open(archive, "r:*") as tf:
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tf, to_)


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
