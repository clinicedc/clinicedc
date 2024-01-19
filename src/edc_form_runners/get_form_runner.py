from __future__ import annotations

from .form_runner import FormRunner
from .site import site_form_runners

__all__ = ["get_form_runner"]


def get_form_runner(model_name: str | None = None, verbose: bool | None = None) -> FormRunner:
    if form_runner_cls := site_form_runners.registry.get(model_name):
        return form_runner_cls(model_name=model_name, verbose=verbose)
    return FormRunner(model_name=model_name, verbose=verbose)
