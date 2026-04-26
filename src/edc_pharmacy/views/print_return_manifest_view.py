from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from ..models import ReturnRequest
from ..pdf_reports import ReturnManifestReport, ReturnNumberedCanvas


def print_return_manifest_view(request, return_request: ReturnRequest | None = None):

    return_request = ReturnRequest.objects.get(pk=return_request)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="return_manifest_{return_request.return_identifier}.pdf"'
    )
    page = dict(
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1.5 * cm,
        pagesize=A4,
    )
    report = ReturnManifestReport(
        return_request=return_request,
        request=request,
        footer_row_height=60,
        page=page,
        numbered_canvas=ReturnNumberedCanvas,
    )

    report.build(response)
    return response
