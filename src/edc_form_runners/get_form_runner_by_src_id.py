from __future__ import annotations

import uuid

from .form_runner_by_scr_id import BaseFormRunnerBySrcId, FormRunnerBySrcId
from .site import site_form_runners

__all__ = ["get_form_runner_by_src_id"]


def get_form_runner_by_src_id(
    src_id: uuid.UUID | None = None,
    model_name: str | None = None,
    verbose: bool | None = None,
) -> BaseFormRunnerBySrcId | FormRunnerBySrcId:
    if form_runner_cls := site_form_runners.registry.get(model_name):
        return type("CustomFormRunnerBySrcId", (BaseFormRunnerBySrcId, form_runner_cls), {})(
            src_id=src_id, model_name=model_name
        )
    return FormRunnerBySrcId(src_id=src_id, model_name=model_name, verbose=verbose)
