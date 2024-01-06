from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.text import slugify
from django_crypto_fields.fields import BaseField

from .constants import SEARCH_SLUG_SEP

style = color_style()
if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel

    from .model_mixins import SearchSlugModelMixin

    class Model(SearchSlugModelMixin, BaseUuidModel):
        pass


class SearchSlug:
    def __init__(self, obj: Model | SearchSlugModelMixin = None, fields: list[str] = None):
        self.warning = None
        self.slug = ""
        self.model_cls = None
        self.fields = None
        if obj and fields:
            self.model_cls = django_apps.get_model(obj._meta.label_lower)
            self.fields = self.get_safe_fields(fields)
            values = []
            for field in fields:
                value = obj
                for f in field.split("."):
                    value = getattr(value, f)
                values.append(value)
            slugs = [slugify(item or "") for item in values]
            slug = SEARCH_SLUG_SEP.join(slugs)
            if len(slug) > 250:
                self.warning = (
                    f"Warning! Search slug string exceeds 250 chars. See {repr(obj)}\n"
                )
                sys.stdout.write(style.WARNING(self.warning))
            self.slug = slug[:250]

    def get_safe_fields(self, fields):
        encrypted_fields = [
            fld.name for fld in self.model_cls._meta.fields if isinstance(fld, BaseField)
        ]
        return [f for f in fields if f not in encrypted_fields]
