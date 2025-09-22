from __future__ import annotations

from django.utils.text import slugify
from django_crypto_fields.utils import get_encrypted_field_names

SLUG_SEP = "|"


def generate_slug(obj, fields) -> str | None:
    """Returns a slug of the char values of the fields
    listed on the models get_search_slug_fields() method.

    Excludes any encrypted fields if listed.
    """
    slug = None
    if obj and fields:
        values = []
        for field in (f for f in fields if f not in get_encrypted_field_names(obj)):
            v = obj
            for f in field.split("."):
                v = getattr(v, f)
            if isinstance(v, str):
                values.append(v[:50])  # truncate value
        slugs = [slugify(v) for v in list(set(values)) if v]
        slug = SLUG_SEP.join(slugs)[:250]
    return slug
