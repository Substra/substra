import uuid
from typing import List

from pydantic import Field

from substra.sdk import models


class OutputAssetDb(models.OutputAsset):
    key: str = Field(default_factory=uuid.uuid4)
    compute_task_key: str

    @staticmethod
    def allowed_filters() -> List[str]:
        return super().allowed_filters() + ["compute_task_key"]
