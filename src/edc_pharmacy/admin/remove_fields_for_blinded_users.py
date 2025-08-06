from django.core.handlers.wsgi import WSGIRequest
from edc_randomization.blinding import user_is_blinded_from_request

from .list_filters import AssignmentListFilter


def remove_fields_for_blinded_users(request: WSGIRequest, fields: tuple) -> tuple:
    """You need to secure custom SimpleListFilters yourself"""
    if user_is_blinded_from_request(request):
        fields = list(fields)
        for f in fields:
            if isinstance(f, str):
                if "assignment" in f or "lot_no" in f or "lot" in f:
                    fields.remove(f)
            elif isinstance(f, tuple):
                f, _ = f
                if "assignment" in f or "lot_no" in f or "lot" in f:
                    fields.remove(f)
            elif issubclass(f, AssignmentListFilter):
                fields.remove(f)
        fields = tuple(fields)
    return fields
