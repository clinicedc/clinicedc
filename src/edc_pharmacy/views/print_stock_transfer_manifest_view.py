from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from ..models import StockTransfer
from ..pdf_reports import ManifestReport, NumberedCanvas


def print_stock_transfer_manifest_view(request, stock_transfer: StockTransfer | None = None):

    stock_transfer = StockTransfer.objects.get(pk=stock_transfer)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="stock_transfer_{stock_transfer.transfer_identifier}.pdf"'
    )
    page = dict(
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1.5 * cm,
        pagesize=A4,
    )
    report = ManifestReport(
        stock_transfer=stock_transfer,
        request=request,
        footer_row_height=60,
        page=page,
        numbered_canvas=NumberedCanvas,
    )

    report.build(response)
    return response
