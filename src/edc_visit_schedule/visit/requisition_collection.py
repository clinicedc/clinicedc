from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils import get_duplicates
from .forms_collection import FormsCollection, FormsCollectionError

if TYPE_CHECKING:
    from .requisition import Requisition


class RequisitionCollection(FormsCollection):
    def __init__(self, *forms: Requisition, name: str | None = None, **kwargs):
        super().__init__(*forms, name=name, **kwargs)

    @staticmethod
    def collection_is_unique_or_raise(forms: tuple[Requisition]) -> None:
        panels = [f.name for f in forms if f.required]
        if duplicates := get_duplicates(list_items=panels):
            raise FormsCollectionError(
                "Expected be a unique sequence of requisitions/panels. "
                f"Got {sorted(panels)}. Duplicates {sorted(duplicates)}"
            )
