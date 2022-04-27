from typing import Optional, Tuple, Union
from uuid import uuid4

from django.conf import settings

from .crf import Crf
from .requisition import Requisition


class FormsCollectionError(Exception):
    pass


class FormsCollection:
    def __init__(self, *forms: Union[Crf, Requisition], name: Optional[str] = None, **kwargs):
        self._forms: Optional[Tuple[Union[Crf, Requisition]]] = None
        self.name = name or uuid4().hex
        forms = [] if not forms or forms == (None,) else list(forms)

        # exclude any flagged for a site that is not the current
        forms = [f for f in forms if not f.site_ids or settings.SITE_ID in f.site_ids]

        # sort on show order
        try:
            forms.sort(key=lambda x: x.show_order)
        except AttributeError as e:
            raise FormsCollectionError(e) from e

        # check sequence
        seq = [item.show_order for item in forms or []]
        if len(list(set(seq))) != len(seq):
            raise FormsCollectionError(
                f'{self.__class__.__name__} "show order" must be a '
                f"unique sequence. Got {seq}."
            )

        # convert to tuple
        self._forms = tuple(forms)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def __iter__(self):
        return iter(self._forms)

    def __len__(self):
        return len(self._forms)

    def append(self, value):
        if value:
            forms = list(self._forms)
            for item in forms:
                if item.name == value.name:
                    raise FormsCollectionError(
                        f"Append failed. Item is not unique. Got {value.name}"
                    )
            forms.append(value)
            forms.sort(key=lambda x: x.show_order)
            self._forms = forms

    def extend(self, value: Union[tuple, list]):
        if value:
            for v in value:
                self.append(v)
            forms = list(self._forms)
            forms.sort(key=lambda x: x.show_order)
            self._forms = tuple(forms)

    def insert(self, index, value):
        if value:
            forms = list(self._forms)
            for index, item in forms:
                if item.name == value.name:
                    raise FormsCollectionError(
                        f"Insert failed. Item is not unique. Got {value.name}"
                    )
            forms.insert(index, value)
            forms.sort(key=lambda x: x.show_order)
            self._forms = tuple(forms)

    def remove(self, value):
        if value:
            forms = list(self._forms)
            for index, item in enumerate(forms):
                if item.name == value.name:
                    forms.pop(index)
                    self._forms = tuple(forms)
                    break
            else:
                raise FormsCollectionError("Remove failed. Item not found")

    def pop(self, index):
        forms = list(self._forms)
        forms.pop(index)
        self._forms = tuple(forms)

    def insert_last(self, value):
        forms = list(self._forms)
        value.show_order = 100 + max([item.show_order for item in forms or []])
        self.append(value)

    @property
    def forms(self):
        return self._forms
