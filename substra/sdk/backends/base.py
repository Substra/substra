import abc
from typing import List

from substra.sdk.schemas import BackendType


class BaseBackend(abc.ABC):
    @property
    @abc.abstractmethod
    def backend_mode(self) -> BackendType:
        raise NotImplementedError

    @abc.abstractmethod
    def login(self, username, password):
        pass

    @abc.abstractmethod
    def logout(self):
        pass

    @abc.abstractmethod
    def get(self, asset_type, key):
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, asset_type, filters=None, paginated=False):
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, spec, spec_options=None):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, key, spec, spec_options=None):
        raise NotImplementedError

    @abc.abstractmethod
    def add_compute_plan_tasks(self, spec, spec_options):
        raise NotImplementedError

    @abc.abstractmethod
    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def download(self, asset_type, url_field_path, key, destination):
        raise NotImplementedError

    @abc.abstractmethod
    def describe(self, asset_type, key):
        raise NotImplementedError

    @abc.abstractmethod
    def cancel_compute_plan(self, key):
        raise NotImplementedError
