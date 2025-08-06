from __future__ import annotations

from typing import TYPE_CHECKING

from ..views import PdfIntermediateView

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.db.models import QuerySet


def print_selected_to_pdf_action(modeladmin, request: WSGIRequest, queryset: QuerySet):
    return PdfIntermediateView(request=request, model_pks=[o.id for o in queryset]).get(
        request,
        app_label=modeladmin.model._meta.app_label,
        model_name=modeladmin.model._meta.model_name,
    )
