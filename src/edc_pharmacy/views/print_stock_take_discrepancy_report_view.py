from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm

from ..pdf_reports.stock_take_discrepancy_pdf_report import (
    NumberedCanvas,
    StockTakeDiscrepancyReport,
)


@login_required
def print_stock_take_discrepancy_report_view(request):
    response = HttpResponse(content_type="application/pdf")
    filename = f"stock_take_discrepancy_report_{timezone.now().strftime('%Y-%m-%d_%H%M')}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    page = dict(
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
        pagesize=landscape(A4),
    )
    report = StockTakeDiscrepancyReport(
        request=request,
        footer_row_height=20,
        page=page,
        numbered_canvas=NumberedCanvas,
    )
    report.build(response)
    return response
