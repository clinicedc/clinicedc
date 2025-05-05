from __future__ import annotations

from typing import TYPE_CHECKING

from ..formula import Formula
from .normal_data import NormalData

if TYPE_CHECKING:
    from .reference_range_collection import ReferenceRangeCollection


def update_normal_data(
    reference_range_collection: ReferenceRangeCollection,
    normal_data: dict[str, list[Formula]] | None = None,
):
    NormalData.objects.filter(reference_range_collection=reference_range_collection).delete()
    for label, formulas in normal_data.items():
        for formula in formulas:
            NormalData.objects.create(
                reference_range_collection=reference_range_collection,
                label=label,
                description=formula.description,
                **formula.__dict__,
            )
