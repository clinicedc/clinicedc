from __future__ import annotations

from django.core.checks import Error

from .utils import ResultModelPanelError, get_result_models_by_panel_name


def result_model_panel_check(app_configs: object, **kwargs: object) -> list:
    """Check that no two result CRFs declare the same lab panel.

    The panel name is used to find the result CRF for an imported
    lab result, so the map must be unambiguous.
    """
    errors: list = []
    try:
        get_result_models_by_panel_name()
    except ResultModelPanelError as e:
        errors.append(
            Error(
                str(e),
                hint="Remove or change `lab_panel` on one of these models.",
                id="edc_lab_results.E010",
            )
        )
    return errors
