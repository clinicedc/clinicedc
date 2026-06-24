from __future__ import annotations

from io import BytesIO

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from ..models import CrfMetadata, CrfMetadataUnavailable
from .review_outstanding_grid_view import ReviewOutstandingGridView, visit_columns

XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


class ExportLeaderboardView(ReviewOutstandingGridView):
    """Export the CRF leaderboard, respecting the current filters, as .xlsx.

    Subclasses the board so all filter parsing and ``leaderboard()`` are reused.
    """

    def get(self, request, *args, **kwargs):  # noqa: ARG002
        visit_schedule_name, schedule_name = self.selected_schedule()
        if not visit_schedule_name:
            return HttpResponseRedirect(reverse("edc_metadata:review_grid_url"))
        site_ids = self.selected_site_ids()
        columns = visit_columns(visit_schedule_name, schedule_name)
        models = self.selected_models()
        subject_q = self.request.GET.get("q", "").strip()
        crf_base = self.base_filter(
            site_ids,
            visit_schedule_name,
            schedule_name,
            self.request.GET.get("visit_code") or None,
            subject_q,
        )
        if models:
            crf_base["model__in"] = models
        crf_exclude = self._flagged_ids(CrfMetadata, CrfMetadataUnavailable, crf_base)
        leaderboard = self.leaderboard(
            site_ids,
            visit_schedule_name,
            schedule_name,
            models,
            columns,
            subject_q,
            crf_exclude,
        )
        return self._xlsx(leaderboard, columns, schedule_name)

    @staticmethod
    def _xlsx(leaderboard, columns, schedule_name) -> HttpResponse:
        from openpyxl import Workbook  # noqa: PLC0415
        from openpyxl.styles import Font  # noqa: PLC0415

        wb = Workbook()
        ws = wb.active
        ws.title = "Leaderboard"
        ws.append(["CRF", *[code for code, _ in columns], "Total"])
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for row in leaderboard:
            ws.append(
                [row["verbose_name"], *[c["count"] for c in row["cells"]], row["total"]]
            )
        stream = BytesIO()
        wb.save(stream)
        response = HttpResponse(stream.getvalue(), content_type=XLSX_CONTENT_TYPE)
        stamp = timezone.now().strftime("%Y%m%d")
        response["Content-Disposition"] = (
            f'attachment; filename="leaderboard_{schedule_name}_{stamp}.xlsx"'
        )
        return response
