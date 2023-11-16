from __future__ import annotations

from typing import TYPE_CHECKING

from .forms_collection import FormsCollection, FormsCollectionError

if TYPE_CHECKING:
    from .requisition import Requisition


class RequisitionCollection(FormsCollection):
    def __init__(self, *forms: Requisition, name: str | None = None, **kwargs):
        super().__init__(*forms, name=name, **kwargs)

    @staticmethod
    def collection_is_unique_or_raise(forms):
        panels = [f.name for f in forms if f.required]
        if len(panels) != len(set(panels)):
            raise FormsCollectionError(
                f"Expected be a unique sequence of requisitions/panels. Got {panels}."
            )
