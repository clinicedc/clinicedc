from __future__ import annotations

from django.utils.text import slugify
from django_crypto_fields.utils import get_encrypted_field_names

from .constants import SEARCH_SLUG_SEP


def generate_slug(obj, fields) -> str | None:
    slug = None
    if obj and fields:
        fields = (f for f in fields if f not in get_encrypted_field_names(obj.__class__))
        values = []
        for field in fields:
            v = obj
            for f in field.split("."):
                v = getattr(v, f)
            if isinstance(v, str):
                values.append(v[:50])  # truncate value
        slugs = [slugify(item or "") for item in values]
        slug = SEARCH_SLUG_SEP.join(slugs)
        slug = slug[:250]
    return slug
