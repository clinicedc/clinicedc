from __future__ import annotations

from typing import TYPE_CHECKING

from .form_runner import FormRunner

if TYPE_CHECKING:
    import uuid


class BaseFormRunnerBySrcId:
    def __init__(
        self, src_id: uuid.UUID, model_name: str | None, verbose: bool | None = None
    ) -> None:
        self.src_id = src_id
        super().__init__(
            src_filter_options=dict(id=self.src_id),
            model_name=model_name,
            verbose=verbose,
        )

    def run_one(self) -> None:
        src_obj = self.src_model_cls.objects.get(id=self.src_id)
        super().run_one(src_obj)


class FormRunnerBySrcId(BaseFormRunnerBySrcId, FormRunner):
    def __init__(self, src_id: uuid.UUID, model_name: str | None, verbose: bool | None = None):
        super().__init__(src_id=src_id, model_name=model_name, verbose=verbose)
