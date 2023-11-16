from __future__ import annotations

from typing import TYPE_CHECKING

from .forms_collection import FormsCollection, FormsCollectionError

if TYPE_CHECKING:
    from .crf import Crf


class CrfCollection(FormsCollection):
    def __init__(self, *forms: Crf, name: str | None = None, **kwargs):
        super().__init__(*forms, name=name, **kwargs)

    @staticmethod
    def collection_is_unique_or_raise(forms):
        models = [f.model for f in forms if f.required]
        if len(models) != len(set(models)):
            raise FormsCollectionError(
                f"Expected be a unique sequence of crf/models. Got {models}."
            )
