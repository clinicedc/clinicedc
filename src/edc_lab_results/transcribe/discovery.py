from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.apps import apps

from ..model_mixins import BloodResultsModelMixin

if TYPE_CHECKING:
    from django.db import models

    from edc_lab import RequisitionPanel

logger = logging.getLogger(__name__)


@dataclass
class CrfInfo:
    """Holds the CRF model class, its associated panel, and the
    utest_ids that panel covers."""

    model: type[models.Model]
    panel: RequisitionPanel
    panel_name: str
    utest_ids: list[str] = field(default_factory=list)


def _normalize_utest_ids(
    raw_utest_ids: tuple | list | None,
) -> list[str]:
    """Extract plain utest_id strings from panel.utest_ids.

    Panel utest_ids entries can be:
      - a plain string: "haemoglobin"
      - a tuple: ("haemoglobin", "Haemoglobin")  (id, verbose_name)
    """
    if not raw_utest_ids:
        return []
    result = []
    for item in raw_utest_ids:
        if isinstance(item, (list, tuple)):
            result.append(item[0])
        else:
            result.append(item)
    return result


def discover_crf_models() -> dict[str, CrfInfo]:
    """Discover all concrete models subclassing BloodResultsModelMixin.

    Returns a mapping of panel_name → CrfInfo.
    """
    crf_models: dict[str, CrfInfo] = {}
    for model in apps.get_models():
        if (
            issubclass(model, BloodResultsModelMixin)
            and not model._meta.abstract  # noqa: SLF001
            and hasattr(model, "lab_panel")
            and model.lab_panel is not None
        ):
            panel = model.lab_panel
            panel_name = panel.name
            utest_ids = _normalize_utest_ids(panel.utest_ids)
            if panel_name in crf_models:
                logger.warning(
                    "Panel '%s' already mapped to %s, skipping %s",
                    panel_name,
                    crf_models[panel_name].model._meta.label,  # noqa: SLF001
                    model._meta.label,  # noqa: SLF001
                )
                continue
            crf_models[panel_name] = CrfInfo(
                model=model,
                panel=panel,
                panel_name=panel_name,
                utest_ids=utest_ids,
            )
    return crf_models


def build_utest_to_panel_map(
    crf_models: dict[str, CrfInfo] | None = None,
) -> dict[str, str]:
    """Invert panel→utest_ids to get utest_id→panel_name.

    Logs a warning if a utest_id appears in multiple panels.
    """
    if crf_models is None:
        crf_models = discover_crf_models()
    utest_map: dict[str, str] = {}
    for panel_name, info in crf_models.items():
        for utest_id in info.utest_ids:
            if utest_id in utest_map:
                logger.warning(
                    "utest_id '%s' found in panels '%s' and '%s'. "
                    "Using first encountered: '%s'.",
                    utest_id,
                    utest_map[utest_id],
                    panel_name,
                    utest_map[utest_id],
                )
            else:
                utest_map[utest_id] = panel_name
    return utest_map
