from substra.sdk.backends.local.compute.spawner.base import BaseSpawner
from substra.sdk.backends.local.compute.spawner.docker import Docker
from substra.sdk.backends.local.compute.spawner.subprocess import Subprocess
from substra.sdk.schemas import BackendType

__all__ = ["BaseSpawner", "Docker", "Subprocess"]

DEBUG_SPAWNER_CHOICES = {
    BackendType.LOCAL_DOCKER: Docker,
    BackendType.LOCAL_SUBPROCESS: Subprocess,
}


def get(name, *args, **kwargs):
    """Return a Docker spawner or a Subprocess spawner"""
    return DEBUG_SPAWNER_CHOICES[name](*args, **kwargs)
