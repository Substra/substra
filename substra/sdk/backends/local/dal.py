import logging
import pathlib
import shutil
import tempfile
import typing

from substra.sdk import exceptions
from substra.sdk import models
from substra.sdk import schemas
from substra.sdk.backends.local import db
from substra.sdk.backends.remote import backend

logger = logging.getLogger(__name__)


class DataAccess:
    """Data access layer.

    This is an intermediate layer between the backend and the local/remote data access.
    """

    def __init__(self, remote_backend: typing.Optional[backend.Remote], local_worker_dir: pathlib.Path):
        self._db = db.get_db()
        self._remote = remote_backend
        self._tmp_dir = tempfile.TemporaryDirectory(prefix=str(local_worker_dir) + "/")

    @property
    def tmp_dir(self):
        return pathlib.Path(self._tmp_dir.name)

    def is_local(self, key: str, type_: schemas.Type):
        try:
            self._db.get(type_, key)
            return True
        except exceptions.NotFound:
            return False

    def _get_asset_content_filename(self, type_):
        if type_ == schemas.Type.Function:
            filename = "function.tar.gz"
            field_name = "archive"

        elif type_ == schemas.Type.Dataset:
            filename = "opener.py"
            field_name = "opener"

        else:
            raise ValueError(f"Cannot download this type of asset {type_}")

        return filename, field_name

    def login(self, username, password):
        if self._remote:
            self._remote.login(username, password)

    def logout(self):
        if self._remote:
            self._remote.logout()

    def add(self, asset):
        return self._db.add(asset)

    def remote_download(self, asset_type, url_field_path, key, destination):
        self._remote.download(asset_type, url_field_path, key, destination)

    def remote_download_model(self, key, destination_file):
        self._remote.download_model(key, destination_file)

    def get_remote_description(self, asset_type, key):
        return self._remote.describe(asset_type, key)

    def get_with_files(self, type_: schemas.Type, key: str):
        """Get the asset with files on the local disk for execution.
        This does not load the description as it is not required for execution.
        """
        try:
            # Try to find the asset locally
            return self._db.get(type_, key)
        except exceptions.NotFound:
            if self._remote is not None:
                # if not found, try remotely
                filename, field_name = self._get_asset_content_filename(type_)
                asset = self._remote.get(type_, key)
                tmp_directory = self.tmp_dir / key
                asset_path = tmp_directory / filename

                if not tmp_directory.exists():
                    pathlib.Path.mkdir(tmp_directory)

                    self._remote.download(
                        type_,
                        field_name + ".storage_address",
                        key,
                        asset_path,
                    )

                attr = getattr(asset, field_name)
                attr.storage_address = asset_path
                return asset
            raise

    def get(self, type_, key: str):
        try:
            # Try to find the asset locally
            return self._db.get(type_, key)
        except exceptions.NotFound:
            if self._remote is not None:
                return self._remote.get(type_, key)
            raise

    def get_performances(self, key: str) -> models.Performances:
        """Get the performances of a given compute. Return models.Performances() object
        easily convertible to dict, filled by the performances data of done tasks that output a performance.
        """
        compute_plan = self.get(schemas.Type.ComputePlan, key)
        list_tasks = self.list(
            schemas.Type.Task,
            filters={"compute_plan_key": [key]},
            order_by="rank",
            ascending=True,
        )

        performances = models.Performances()

        for task in list_tasks:
            if task.status == models.ComputeTaskStatus.done:
                function = self.get(schemas.Type.Function, task.function.key)
                perf_identifiers = [
                    output.identifier for output in function.outputs if output.kind == schemas.AssetKind.performance
                ]
                outputs = self.list(
                    schemas.Type.OutputAsset, {"compute_task_key": task.key, "identifier": perf_identifiers}
                )
                for output in outputs:
                    performances.compute_plan_key.append(compute_plan.key)
                    performances.compute_plan_tag.append(compute_plan.tag)
                    performances.compute_plan_status.append(compute_plan.status)
                    performances.compute_plan_start_date.append(compute_plan.start_date)
                    performances.compute_plan_end_date.append(compute_plan.end_date)
                    performances.compute_plan_metadata.append(compute_plan.metadata)

                    performances.worker.append(task.worker)
                    performances.task_key.append(task.key)
                    performances.task_rank.append(task.rank)
                    try:
                        round_idx = int(task.metadata.get("round_idx"))
                    except TypeError:
                        round_idx = None
                    performances.round_idx.append(round_idx)
                    performances.identifier.append(output.identifier)
                    performances.performance.append(output.asset)

        return performances

    def list(
        self, type_: str, filters: typing.Dict[str, typing.List[str]], order_by: str = None, ascending: bool = False
    ):
        """Joins the results of the [local db](substra.sdk.backends.local.db.list) and the
        [remote db](substra.sdk.backends.rest_client.list) in hybrid mode.
        """

        local_assets = self._db.list(type_=type_, filters=filters, order_by=order_by, ascending=ascending)

        remote_assets = []
        if self._remote:
            try:
                remote_assets = self._remote.list(
                    asset_type=type_, filters=filters, order_by=order_by, ascending=ascending
                )
            except Exception as e:
                logger.info(
                    f"Could not list assets from the remote platform:\n{e}. \
                    \nIf you are not logged to a remote platform, ignore this message."
                )
        return local_assets + remote_assets

    def save_file(self, file_path: typing.Union[str, pathlib.Path], key: str):
        """Copy file or directory into the local temp dir to mimick
        the remote backend that saves the files given by the user.
        """
        tmp_directory = self.tmp_dir / key
        tmp_file = tmp_directory / pathlib.Path(file_path).name

        if not tmp_directory.exists():
            pathlib.Path.mkdir(tmp_directory)

        if tmp_file.exists():
            raise exceptions.AlreadyExists(f"File {tmp_file.name} already exists for asset {key}", 409)
        elif pathlib.Path(file_path).is_file():
            shutil.copyfile(file_path, tmp_file)
        elif pathlib.Path(file_path).is_dir():
            shutil.copytree(file_path, tmp_file)
        else:
            raise exceptions.InvalidRequest(f"Could not copy {file_path}", 400)
        return tmp_file

    def update(self, asset):
        self._db.update(asset)
        return
