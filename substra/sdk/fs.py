import os

from substra.sdk.hasher import Hasher

_BLOCK_SIZE = 64 * 1024


def hash_file(path):
    """Hash a file."""
    hasher = Hasher()

    with open(path, "rb") as fp:
        while True:
            data = fp.read(_BLOCK_SIZE)
            if not data:
                break
            hasher.update(data)
    return hasher.compute()


def hash_directory(path, followlinks=False):
    """Hash a directory."""

    if not os.path.isdir(path):
        raise TypeError(f"{path} is not a directory.")

    hash_values = []
    for root, dirs, files in os.walk(path, topdown=True, followlinks=followlinks):
        dirs.sort()
        files.sort()

        for fname in files:
            hash_values.append(hash_file(os.path.join(root, fname)))

    return Hasher(values=sorted(hash_values)).compute()
