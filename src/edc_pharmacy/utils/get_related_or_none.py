from __future__ import annotations

from django.core.exceptions import ObjectDoesNotExist


def get_related_or_none(obj, attr):
    try:
        return getattr(obj, attr)
    except ObjectDoesNotExist:
        return None
