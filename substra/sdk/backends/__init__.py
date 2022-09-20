from substra.sdk import schemas
from substra.sdk.backends.local.backend import Local
from substra.sdk.backends.remote.backend import Remote

_BACKEND_CHOICES = {
    schemas.BackendType.REMOTE: Remote,
    schemas.BackendType.LOCAL_DOCKER: Local,
    schemas.BackendType.LOCAL_SUBPROCESS: Local,
}


def get(name, *args, **kwargs):
    return _BACKEND_CHOICES[name](*args, **kwargs, backend_type=name)
