from uuid import UUID

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm

from ..models import Stock
from ..pdf_reports import NumberedCanvas as BaseNumberedCanvas
from ..pdf_reports import StockReport


class NumberedCanvas(BaseNumberedCanvas):
    footer_row_height = 20
    pagesize = landscape(A4)


def print_stock_view(request, session_uuid: UUID | None):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="stock_report.pdf"'
    page = dict(
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
        pagesize=landscape(A4),
    )
    pks = []
    if session_uuid:
        pks = request.session.get(str(session_uuid))
    queryset = Stock.objects.filter(pk__in=pks)
    report = StockReport(
        queryset=queryset,
        request=request,
        footer_row_height=20,
        page=page,
        numbered_canvas=NumberedCanvas,
    )

    report.build(response)
    return response
