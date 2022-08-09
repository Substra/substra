from substra.sdk.backends.local.backend import Local
from substra.sdk.backends.remote.backend import Remote

_BACKEND_CHOICES = {
    "remote": Remote,
    "local": Local,
}


def get(name, *args, **kwargs):
    return _BACKEND_CHOICES[name.lower()](*args, **kwargs)
