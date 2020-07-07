import abc


class BaseBackend(abc.ABC):

    def login(self, uername, password):
        pass

    def get(self, asset_type, key):
        raise NotImplementedError

    def list(self, asset_type, filters=None):
        raise NotImplementedError

    def add(self, spec, exist_ok=False, spec_options=None):
        raise NotImplementedError

    def update_compute_plan(self, compute_plan_id, spec):
        raise NotImplementedError

    def link_dataset_with_objective(self, dataset_key, objective_key):
        raise NotImplementedError

    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys):
        raise NotImplementedError

    def download(self, asset_type, url_field_path, key, destination):
        raise NotImplementedError

    def describe(self, asset_type, key):
        raise NotImplementedError

    def leaderboard(self, objective_key, sort='desc'):
        raise NotImplementedError

    def cancel_compute_plan(self, compute_plan_id):
        raise NotImplementedError
