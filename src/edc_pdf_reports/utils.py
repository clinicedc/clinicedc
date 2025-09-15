from __future__ import annotations

from io import BytesIO
from tempfile import mkdtemp
from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.db.models import QuerySet
from pypdf import PdfWriter

from .numbered_canvas import NumberedCanvas

if TYPE_CHECKING:
    from .model_mixins import PdfReportModelMixin

    class Model(PdfReportModelMixin, models.Model): ...


mkdtemp()


def write_queryset_to_secure_pdf(
    queryset: QuerySet | None = None,
    password: str | None = None,
    request: WSGIRequest | None = None,
    **extra_context,
) -> BytesIO:
    """Merges one or more PDF buffers into a single secure PDF buffer
    with a password.

    Pass PDF buffer to FileResponse or write to file.
    """
    merger = PdfWriter()
    for model_obj in queryset:
        buffer = write_model_to_insecure_pdf(model_obj, request=request, **extra_context)
        merger.append(fileobj=buffer)
        buffer.close()
    merged_buffer = BytesIO()
    merger.encrypt(password, algorithm="AES-256")
    merger.write(merged_buffer)
    merged_buffer.seek(0)
    return merged_buffer


def write_model_to_insecure_pdf(
    model_obj: Model, request: WSGIRequest | None = None, **extra_context
) -> BytesIO:
    pdf_report = model_obj.pdf_report_cls(
        model_obj=model_obj, request=request, **extra_context
    )
    buffer = BytesIO()
    doctemplate = pdf_report.document_template(buffer, **pdf_report.page)
    story = pdf_report.get_report_story()
    doctemplate.build(
        story,
        onFirstPage=pdf_report.on_first_page,
        onLaterPages=pdf_report.on_later_pages,
        canvasmaker=NumberedCanvas,
    )
    buffer.seek(0)
    return buffer
