from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from django.apps import apps as django_apps

if TYPE_CHECKING:
    from django.db import models

__all__ = [
    "ResultModelPanelError",
    "get_decimal_places",
    "get_result_model_cls",
    "get_result_models_by_panel_name",
    "get_utest_ids",
]


class ResultModelPanelError(Exception):
    pass


@cache
def _registry() -> dict[str, type[models.Model]]:
    """Return {panel name: result CRF model class} for all installed apps.

    A result CRF is any concrete model that declares `lab_panel` on
    `CrfWithRequisitionModelMixin` and is linked to a related visit.
    Models that declare `lab_panel` without these mixins, for example
    calculation-only helpers, are ignored.

    The panel name is read from the `RequisitionPanel` object, not from
    the `edc_lab.Panel` model instance, so this does not touch the DB
    and is safe to build before or during a system check.
    """
    # imported here, `utils` is imported by `apps` before models load
    from edc_lab.model_mixins import CrfWithRequisitionModelMixin  # noqa: PLC0415

    registry: dict[str, type[models.Model]] = {}
    for model_cls in django_apps.get_models():
        lab_panel = getattr(model_cls, "lab_panel", None)
        if (
            lab_panel is None
            or not issubclass(model_cls, CrfWithRequisitionModelMixin)
            or not hasattr(model_cls, "related_visit_model_attr")
        ):
            continue
        if registered_cls := registry.get(lab_panel.name):
            raise ResultModelPanelError(
                "More than one result CRF declares this lab panel. "
                f"Got panel '{lab_panel.name}' on "
                f"'{registered_cls._meta.label_lower}' and "
                f"'{model_cls._meta.label_lower}'. "
                "See attr `lab_panel` on each model."
            )
        registry.update({lab_panel.name: model_cls})
    return registry


def get_result_models_by_panel_name() -> dict[str, type[models.Model]]:
    """Return a copy of the {panel name: result CRF model class} map."""
    return dict(_registry())


def get_result_model_cls(panel_name: str | None) -> type[models.Model] | None:
    """Return the result CRF model class for this panel name, or None."""
    if not panel_name:
        return None
    return _registry().get(panel_name)


@cache
def get_utest_ids(model_cls: type[models.Model]) -> tuple[str, ...]:
    """Return the utest ids on this result CRF, in field order.

    A utest id is read from the value field of each result, for example
    field `haemoglobin_value` gives utest id `haemoglobin`. See also
    `reportable_result_model_mixin_factory`.
    """
    suffix = "_value"
    return tuple(
        fld_cls.name[: -len(suffix)]
        for fld_cls in model_cls._meta.get_fields()
        if fld_cls.name.endswith(suffix)
    )


@cache
def get_decimal_places(model_cls: type[models.Model]) -> dict[str, int | None]:
    """Return {utest id: decimal_places} for the value field of each
    result on this result CRF.

    The value is None where the value field is not a `DecimalField`,
    in which case the value has no stored precision to round to.
    """
    return {
        utest_id: getattr(
            model_cls._meta.get_field(f"{utest_id}_value"), "decimal_places", None
        )
        for utest_id in get_utest_ids(model_cls)
    }


def clear_result_model_cache(setting: str | None = None, **kwargs) -> None:
    """Clear the cached registry.

    Connected to `setting_changed` since tests may override
    INSTALLED_APPS, which changes the models django reports.
    """
    if setting is None or setting == "INSTALLED_APPS":
        _registry.cache_clear()
        get_utest_ids.cache_clear()
        get_decimal_places.cache_clear()
