import hashlib


class Hasher:
    def __init__(self, values=None):
        self._h = hashlib.sha256()
        if values:
            for v in values:
                self.update(v)

    def update(self, v):
        if isinstance(v, str):
            v = v.encode("utf-8")
        self._h.update(v)

    def compute(self):
        return self._h.hexdigest()
