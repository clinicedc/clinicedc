from django.core.handlers.wsgi import WSGIRequest

from edc_randomization.blinding import user_is_blinded_from_request

from .list_filters import AssignmentListFilter


def remove_fields_for_blinded_users(
    request: WSGIRequest, fields: tuple
) -> tuple[str | tuple | type[AssignmentListFilter], ...]:
    """You need to secure custom SimpleListFilters yourself"""
    if user_is_blinded_from_request(request):
        fields: list[str | tuple | type[AssignmentListFilter]] = list(fields)
        for fld in fields:
            if isinstance(fld, str):
                if "assignment" in fld or "lot_no" in fld or "lot" in fld:
                    fields.remove(fld)
            elif isinstance(fld, tuple):
                f, _ = fld
                if "assignment" in f or "lot_no" in f or "lot" in f:
                    fields.remove(fld)
            elif issubclass(fld, AssignmentListFilter):
                fields.remove(fld)
    return tuple(fields)
