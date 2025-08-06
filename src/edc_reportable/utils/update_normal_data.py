from __future__ import annotations

from typing import TYPE_CHECKING

from ..formula import Formula
from .normal_data_model_cls import normal_data_model_cls

if TYPE_CHECKING:
    from ..models import ReferenceRangeCollection


def update_normal_data(
    reference_range_collection: ReferenceRangeCollection,
    normal_data: dict[str, list[Formula]] | None = None,
):
    normal_data_model_cls().objects.filter(
        reference_range_collection=reference_range_collection
    ).delete()
    for label, formulas in normal_data.items():
        for formula in formulas:
            opts = {k: v for k, v in formula.__dict__.items() if k != "gender"}
            for gender in formula.__dict__.get("gender"):
                normal_data_model_cls().objects.create(
                    reference_range_collection=reference_range_collection,
                    label=label,
                    gender=gender,
                    **opts,
                )
