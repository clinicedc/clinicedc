"""PDF report for printing a Purchase Order to send to a supplier.

Layout:
  - Top-strip: 'PURCHASE ORDER' (left), protocol name (right)
  - Two-column metadata block: Reference / Date / Status (left),
                               Supplier / Ship-to (right)
  - Items table: identifier, product, container, units/container,
                 containers ordered, units ordered
  - Notes / comment box
  - Signature line
"""

from __future__ import annotations

from django.utils.translation import gettext as _
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from edc_pdf_reports import NumberedCanvas as BaseNumberedCanvas
from edc_pdf_reports import Report
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils.date import to_local

from ..models import Location, Order


class NumberedCanvas(BaseNumberedCanvas):
    footer_row_height = 60


class OrderReport(Report):
    def __init__(self, order: Order = None, **kwargs):
        self.order = order
        self.protocol_name = ResearchProtocolConfig().protocol_title
        super().__init__(**kwargs)

    def draw_header(self, canvas, doc):  # noqa: ARG002
        width, height = A4
        canvas.setFontSize(6)
        text_width = stringWidth(self.protocol_name, "Helvetica", 6)
        canvas.drawRightString(width - text_width, height - 20, self.protocol_name.upper())
        canvas.drawString(
            40,
            height - 30,
            (
                _("Purchase Order: %(order_identifier)s")
                % {"order_identifier": self.order.order_identifier}
            ).upper(),
        )

    @property
    def queryset(self):
        return self.order.orderitem_set.select_related(
            "product", "container"
        ).order_by("order_item_identifier")

    @staticmethod
    def _ship_to_location() -> Location | None:
        """Central pharmacy is the first Location with no site (matches the
        filter used elsewhere for receive locations)."""
        return Location.objects.filter(site__isnull=True).first()

    def get_report_story(self, document_template: SimpleDocTemplate = None, **kwargs):  # noqa: ARG002
        story = []

        title_style = ParagraphStyle(
            "Title",
            fontSize=12,
            spaceAfter=0,
            alignment=TA_LEFT,
            fontName="Helvetica-Bold",
        )
        protocol_style = ParagraphStyle(
            "Protocol",
            fontSize=10,
            spaceAfter=0,
            alignment=TA_RIGHT,
            fontName="Helvetica-Bold",
        )
        story.append(
            Table(
                [
                    [
                        Paragraph(_("Purchase Order").upper(), title_style),
                        Paragraph(self.protocol_name.upper(), protocol_style),
                    ]
                ]
            )
        )
        story.append(Spacer(0.1 * cm, 0.4 * cm))

        story.append(self._meta_block_as_table())
        story.append(Spacer(0.1 * cm, 0.4 * cm))

        story.append(self._addresses_block_as_table())
        story.append(Spacer(0.1 * cm, 0.4 * cm))

        story.append(self._items_as_table())
        story.append(Spacer(0.1 * cm, 0.5 * cm))

        if self.order.comment:
            story.append(self._comment_box_as_table())
            story.append(Spacer(0.1 * cm, 0.4 * cm))

        story.append(self._signature_line_as_table())

        return story

    # ── Sections ────────────────────────────────────────────────────────

    def _meta_block_as_table(self) -> Table:
        bold_left = ParagraphStyle(
            "bl", alignment=TA_LEFT, fontSize=9, fontName="Helvetica-Bold"
        )
        left = ParagraphStyle("l", alignment=TA_LEFT, fontSize=9)
        order_date = to_local(self.order.order_datetime).strftime("%d-%b-%Y")
        item_count = self.queryset.count()
        data = [
            [
                Paragraph(_("Order #:"), bold_left),
                Paragraph(self.order.order_identifier or "—", left),
                Paragraph(_("Order date:"), bold_left),
                Paragraph(order_date, left),
            ],
            [
                Paragraph(_("Title:"), bold_left),
                Paragraph(self.order.title or "—", left),
                Paragraph(_("Items:"), bold_left),
                Paragraph(str(item_count), left),
            ],
            [
                Paragraph(_("Status:"), bold_left),
                Paragraph(self.order.get_status_display(), left),
                Paragraph("", left),
                Paragraph("", left),
            ],
        ]
        col_label = stringWidth(_("Order date:"), "Helvetica", 9) + 6
        return Table(
            data,
            colWidths=(col_label, None, col_label, None),
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        )

    def _addresses_block_as_table(self) -> Table:
        header_style = ParagraphStyle(
            "h", fontSize=9, fontName="Helvetica-Bold", alignment=TA_LEFT
        )
        body_style = ParagraphStyle("b", fontSize=9, alignment=TA_LEFT, leading=11)

        supplier_lines = self._format_supplier_lines()
        ship_to_lines = self._format_ship_to_lines()

        cells = [
            [
                Paragraph(_("Supplier").upper(), header_style),
                Paragraph(_("Ship to").upper(), header_style),
            ],
            [
                Paragraph("<br/>".join(supplier_lines) or "—", body_style),
                Paragraph("<br/>".join(ship_to_lines) or "—", body_style),
            ],
        ]
        table = Table(cells, colWidths=(None, None))
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _format_supplier_lines(self) -> list[str]:
        s = self.order.supplier
        if not s:
            return []
        lines = [str(s.name)]
        if s.contact:
            lines.append(f"Attn: {s.contact}")
        addr_lines = [s.address_one, s.address_two]
        for line in addr_lines:
            if line and line != "-":
                lines.append(line)
        city_state_zip = ", ".join(
            x for x in [s.city, getattr(s, "state", ""), getattr(s, "postal_code", "")]
            if x and x != "-"
        )
        if city_state_zip:
            lines.append(city_state_zip)
        if s.country and s.country != "-":
            lines.append(s.country)
        if s.telephone and s.telephone != "-":
            lines.append(f"Tel: {s.telephone}")
        if s.email and s.email != "-":
            lines.append(f"Email: {s.email}")
        return lines

    def _format_ship_to_lines(self) -> list[str]:
        loc = self._ship_to_location()
        if not loc:
            return []
        lines = [loc.display_name]
        if loc.contact_name:
            lines.append(f"Attn: {loc.contact_name}")
        if loc.contact_tel:
            lines.append(f"Tel: {loc.contact_tel}")
        if loc.contact_email:
            lines.append(f"Email: {loc.contact_email}")
        return lines

    def _items_as_table(self) -> Table:
        header_style = ParagraphStyle(
            "h",
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.black,
            fontName="Helvetica-Bold",
        )
        cell_left = ParagraphStyle("cl", alignment=TA_LEFT, fontSize=8, leading=10)
        cell_right = ParagraphStyle("cr", alignment=TA_RIGHT, fontSize=8, leading=10)

        rows = [
            [
                Paragraph(_("Item #"), header_style),
                Paragraph(_("Product"), header_style),
                Paragraph(_("Assignment"), header_style),
                Paragraph(_("Quantity"), header_style),
                Paragraph(_("Unit"), header_style),
            ]
        ]
        for oi in self.queryset:
            unit = oi.container.name if oi.container else "—"
            assignment = (
                str(oi.product.assignment)
                if oi.product and oi.product.assignment
                else "—"
            )
            rows.append(
                [
                    Paragraph(oi.order_item_identifier or "—", cell_left),
                    Paragraph(oi.product.name if oi.product else "—", cell_left),
                    Paragraph(assignment, cell_left),
                    Paragraph(f"{oi.unit_qty_ordered:,}", cell_right),
                    Paragraph(unit, cell_left),
                ]
            )

        table = Table(
            rows,
            colWidths=(2.5 * cm, 6.5 * cm, 2.5 * cm, 3 * cm, 3.5 * cm),
            repeatRows=1,
        )
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        return table

    def _comment_box_as_table(self) -> Table:
        header_style = ParagraphStyle(
            "h", fontSize=9, fontName="Helvetica-Bold", alignment=TA_LEFT
        )
        body_style = ParagraphStyle("b", fontSize=9, alignment=TA_LEFT, leading=11)
        table = Table(
            [
                [Paragraph(_("Notes").upper(), header_style)],
                [Paragraph(self.order.comment.replace("\n", "<br/>"), body_style)],
            ],
            colWidths=(None,),
        )
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        return table

    def _signature_line_as_table(self) -> Table:
        label_style = ParagraphStyle(
            "l", fontSize=9, fontName="Helvetica-Bold", alignment=TA_LEFT
        )
        line_style = ParagraphStyle(
            "ln", fontSize=9, alignment=TA_LEFT, textColor=colors.lightgrey
        )
        rows = [
            [
                Paragraph(_("Authorised by:"), label_style),
                Paragraph("_______________________________", line_style),
                Paragraph(_("Date:"), label_style),
                Paragraph("________________", line_style),
            ],
            [
                Paragraph(_("Signature:"), label_style),
                Paragraph("_______________________________", line_style),
                Paragraph("", label_style),
                Paragraph("", line_style),
            ],
        ]
        col_label = stringWidth(_("Authorised by:"), "Helvetica-Bold", 9) + 8
        return Table(
            rows,
            colWidths=(col_label, None, col_label, 3.5 * cm),
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        )
