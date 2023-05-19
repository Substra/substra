import uuid
from typing import List

from pydantic import Field

from substra.sdk import models
from substra.sdk import schemas


class _TaskAssetLocal(schemas._PydanticConfig):
    key: str = Field(default_factory=uuid.uuid4)
    compute_task_key: str

    @staticmethod
    def allowed_filters() -> List[str]:
        return super().allowed_filters() + ["compute_task_key"]


class OutputAssetLocal(models.OutputAsset, _TaskAssetLocal):
    pass


class InputAssetLocal(models.InputAsset, _TaskAssetLocal):
    pass
