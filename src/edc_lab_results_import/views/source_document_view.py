from __future__ import annotations

from typing import Any

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from ..models import SourceDocument


class SourceDocumentView(PermissionRequiredMixin, View):
    """Serve the original result PDF archived for a `SourceDocument`.

    PDFs hold PII and are archived outside of MEDIA_ROOT, so they are
    never served by the webserver directly. Each request is
    authenticated and checked against `view_sourcedocument`.

    The file is streamed by Django, which sends the whole PDF on every
    request. In production, hand off to the webserver instead by way of
    X-Accel-Redirect (nginx) using `obj.pdf.name`.
    """

    permission_required = "edc_lab_results_import.view_sourcedocument"

    def get(self, request, *args: Any, **kwargs: Any) -> FileResponse:  # noqa: ARG002
        obj = get_object_or_404(SourceDocument, pk=kwargs.get("pk"))
        if not obj.pdf:
            raise Http404(f"Source document has no file. Got {obj.filename}.")
        try:
            fileobj = obj.pdf.open("rb")
        except FileNotFoundError as e:
            raise Http404(
                f"Source document file not found. Got {obj.pdf.name}. "
                "See settings.EDC_LAB_RESULTS_IMPORT_PRIVATE_PATH."
            ) from e
        return FileResponse(
            fileobj,
            content_type="application/pdf",
            filename=obj.filename,
        )
