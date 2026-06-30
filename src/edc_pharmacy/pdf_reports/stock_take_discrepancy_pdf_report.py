from django.utils.timezone import localtime
from django.utils.translation import gettext as _
from reportlab.graphics.barcode import code128
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from edc_pdf_reports import NumberedCanvas as BaseNumberedCanvas
from edc_pdf_reports import Report
from edc_protocol.research_protocol_config import ResearchProtocolConfig

from ..choices import STOCK_TRANSACTION_ABBR, STOCK_TRANSACTION_CHOICES
from ..constants import TXN_BIN_MOVED
from ..models import MISSING, UNEXPECTED, StockTake, StorageBin
from ..utils import last_txn_abbr_by_stock, subject_identifier_by_stock

# Compact action labels for the report (override the verbose choice display).
_ACTION_LABELS = {TXN_BIN_MOVED: "Moved"}


class NumberedCanvas(BaseNumberedCanvas):
    footer_row_height = 20
    pagesize = landscape(A4)


_HEADER_STYLE = ParagraphStyle(
    "col_header", fontSize=8, alignment=TA_CENTER, fontName="Helvetica-Bold"
)
_CELL_STYLE = ParagraphStyle("cell", fontSize=7, alignment=TA_LEFT, leading=9)
_CELL_CENTER = ParagraphStyle("cell_c", fontSize=7, alignment=TA_CENTER, leading=9)
_LOC_STYLE = ParagraphStyle(
    "loc_header", fontSize=9, alignment=TA_LEFT, fontName="Helvetica-Bold"
)


class StockTakeDiscrepancyReport(Report):
    """PDF report of stock take discrepancies, grouped by location."""

    def __init__(self, site_id=None, **kwargs):
        self.protocol_name = ResearchProtocolConfig().protocol_title
        try:
            self.site_id = int(site_id) if site_id else None
        except (TypeError, ValueError):
            self.site_id = None
        super().__init__(**kwargs)

    def draw_header(self, canvas, doc):  # noqa: ARG002
        width, height = self.page.get("pagesize")
        canvas.setFontSize(6)
        text_width = stringWidth(self.protocol_name, "Helvetica", 6)
        canvas.drawRightString(width - text_width, height - 20, self.protocol_name.upper())
        canvas.drawString(40, height - 30, _("Stock Take Discrepancy Report").upper())

    def get_report_story(self, document_template: SimpleDocTemplate = None, **kwargs):  # noqa: ARG002
        story = []

        # Title row
        title_data = [[
            Paragraph(_("Stock Take Discrepancy Report").upper(), ParagraphStyle(
                "title", fontSize=11, alignment=TA_LEFT, fontName="Helvetica-Bold"
            )),
            Paragraph(self.protocol_name.upper(), ParagraphStyle(
                "title_r", fontSize=11, alignment=TA_RIGHT, fontName="Helvetica-Bold"
            )),
        ]]
        story.append(Table(title_data))
        story.append(Spacer(0.1 * cm, 0.4 * cm))

        rows_by_location = self._build_rows()

        if not rows_by_location:
            story.append(Paragraph("No discrepancies found.", _CELL_STYLE))
            return story

        for location_name, (location_obj, rows) in sorted(rows_by_location.items()):
            story.append(Paragraph(location_name, _LOC_STYLE))
            story.append(Spacer(0.1 * cm, 0.15 * cm))
            story.append(self._location_table(rows))
            story.append(Spacer(0.1 * cm, 0.3 * cm))
            story.append(Paragraph(_("Stock Take Summary — All Bins").upper(), _LOC_STYLE))
            story.append(Spacer(0.1 * cm, 0.15 * cm))
            story.append(self._bin_summary_table(location_obj))
            story.append(Spacer(0.1 * cm, 0.5 * cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
            story.append(Spacer(0.1 * cm, 0.3 * cm))

        story.extend(self._legend_flowables())
        return story

    @staticmethod
    def _legend_flowables() -> list:
        """Legend mapping each TXN abbreviation to its full transaction type."""
        pairs = sorted(
            (
                (STOCK_TRANSACTION_ABBR[txn_type], display)
                for txn_type, display in STOCK_TRANSACTION_CHOICES
                if txn_type in STOCK_TRANSACTION_ABBR
            ),
            key=lambda pair: pair[0],
        )
        entries = [f"<b>{abbr}</b>&nbsp;&nbsp;{display}" for abbr, display in pairs]
        # Fill column-major so each column reads alphabetically top-to-bottom.
        ncols = 3
        nrows = -(-len(entries) // ncols)
        columns = [entries[c * nrows : (c + 1) * nrows] for c in range(ncols)]
        grid = [
            [col[r] if r < len(col) else "" for col in columns] for r in range(nrows)
        ]
        data = [[Paragraph(cell, _CELL_STYLE) for cell in grid_row] for grid_row in grid]
        table = Table(data, colWidths=[9 * cm, 9 * cm, 9 * cm])
        table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        return [
            Paragraph(_("TXN — last transaction codes").upper(), _LOC_STYLE),
            Spacer(0.1 * cm, 0.15 * cm),
            table,
        ]

    def _build_rows(self) -> dict[str, tuple]:
        bins = StorageBin.objects.filter(in_use=True)
        if self.site_id:
            bins = bins.filter(location__site_id=self.site_id)
        bins = bins.select_related("container", "location").order_by(
            "location__display_name", "bin_identifier"
        )
        rows_by_location: dict[str, tuple] = {}
        for b in bins:
            last: StockTake | None = (
                StockTake.objects.filter(storage_bin=b)
                .order_by("-stock_take_datetime")
                .first()
            )
            if not last or (last.missing_count == 0 and last.unexpected_count == 0):
                continue
            items = list(
                last.items.filter(status__in=[MISSING, UNEXPECTED])
                .select_related(
                    "stock__product__formulation",
                    "stock_transaction",
                )
                .order_by("status", "code")
            )
            location_name = b.location.display_name or b.location.name
            bin_label = (
                f"{b.name} ({b.bin_identifier})" if b.name else b.bin_identifier
            )
            if location_name not in rows_by_location:
                rows_by_location[location_name] = (b.location, [])
            rows_by_location[location_name][1].extend([
                {
                    "bin": bin_label,
                    "item": item,
                    "stock_take_datetime": last.stock_take_datetime,
                }
                for item in items
            ])
        return rows_by_location

    @staticmethod
    def _action_and_note(item) -> tuple[str, str]:
        """The correction applied to a discrepancy and its audit note.

        Returns ("", "") when the discrepancy is still open.
        """
        if item.resolved:
            txn = item.stock_transaction
            label = _ACTION_LABELS.get(txn.transaction_type) or (
                txn.get_transaction_type_display()
            )
            return label, txn.reason
        if item.acknowledged:
            return _("Acknowledged"), item.acknowledged_note
        return "", ""

    @staticmethod
    def _last_txn_abbr_by_stock(rows: list[dict]) -> dict:
        """Map stock_id -> abbreviation of its most recent transaction_type."""
        return last_txn_abbr_by_stock(row["item"].stock_id for row in rows)

    def _location_table(self, rows: list[dict]) -> Table:
        col_widths = [
            2.0 * cm, 3.5 * cm, 2.8 * cm, 3.6 * cm, 2.2 * cm,
            2.0 * cm, 2.4 * cm, 4.0 * cm, 1.4 * cm,
        ]
        data = [[
            Paragraph(_("BIN"), _HEADER_STYLE),
            Paragraph(_("CODE"), _HEADER_STYLE),
            Paragraph(_("SUBJECT"), _HEADER_STYLE),
            Paragraph(_("PRODUCT"), _HEADER_STYLE),
            Paragraph(_("ISSUE"), _HEADER_STYLE),
            Paragraph(_("STOCK TAKE DATE"), _HEADER_STYLE),
            Paragraph(_("ACTION"), _HEADER_STYLE),
            Paragraph(_("AUDIT NOTE"), _HEADER_STYLE),
            Paragraph(_("TXN"), _HEADER_STYLE),
        ]]

        stock_ids = [row["item"].stock_id for row in rows]
        txn_abbr_by_stock = self._last_txn_abbr_by_stock(rows)
        subject_by_stock = subject_identifier_by_stock(stock_ids)

        for row in rows:
            item = row["item"]
            stock = item.stock

            # Barcode with the human-readable code centered below it, one cell.
            barcode = code128.Code128(item.code, barHeight=5 * mm, barWidth=0.7, gap=1.7)
            code_cell = [barcode, Paragraph(item.code, _CELL_CENTER)]

            # Recipient from the canonical Allocation table (the Stock cache and
            # the sticky-pointer FK are unreliable for terminal/dispensed stock).
            subject_identifier = subject_by_stock.get(item.stock_id, "")

            product_name = ""
            if stock:
                try:
                    product_name = stock.product.formulation.imp_description
                except AttributeError:
                    product_name = str(stock.product) if stock.product else ""

            issue = item.get_status_display()
            take_date = localtime(row["stock_take_datetime"]).strftime("%d-%b-%Y")
            txn_abbr = txn_abbr_by_stock.get(item.stock_id, "")
            action, audit_note = self._action_and_note(item)

            data.append([
                Paragraph(row["bin"], _CELL_CENTER),
                code_cell,
                Paragraph(subject_identifier, _CELL_STYLE),
                Paragraph(product_name, _CELL_STYLE),
                Paragraph(issue, _CELL_CENTER),
                Paragraph(take_date, _CELL_CENTER),
                Paragraph(action, _CELL_CENTER),
                Paragraph(audit_note, _CELL_STYLE),
                Paragraph(txn_abbr, _CELL_CENTER),
            ])

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
        ]))
        return table

    def _bin_summary_table(self, location) -> Table:
        col_widths = [5 * cm, 5 * cm, 4 * cm]
        data = [[
            Paragraph(_("BIN"), _HEADER_STYLE),
            Paragraph(_("LAST STOCK TAKE"), _HEADER_STYLE),
            Paragraph(_("PERFORMED BY"), _HEADER_STYLE),
        ]]
        bins = (
            StorageBin.objects.filter(in_use=True, location=location)
            .select_related("location")
            .order_by("name", "bin_identifier")
        )
        for b in bins:
            last: StockTake | None = (
                StockTake.objects.filter(storage_bin=b)
                .select_related("performed_by")
                .order_by("-stock_take_datetime")
                .first()
            )
            bin_label = f"{b.name} ({b.bin_identifier})" if b.name else b.bin_identifier
            if last:
                take_date = localtime(last.stock_take_datetime).strftime("%d-%b-%Y %H:%M")
                performed_by = last.performed_by.username if last.performed_by else "—"
            else:
                take_date = "—"
                performed_by = "—"
            data.append([
                Paragraph(bin_label, _CELL_STYLE),
                Paragraph(take_date, _CELL_CENTER),
                Paragraph(performed_by, _CELL_CENTER),
            ])

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
        ]))
        return table
