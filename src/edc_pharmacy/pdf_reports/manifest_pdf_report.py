from django.utils.translation import gettext as _
from edc_pdf_reports import NumberedCanvas as BaseNumberedCanvas
from edc_pdf_reports import Report
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils.date import to_local
from reportlab.graphics.barcode import code128
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from ..models import StockTransfer


class NumberedCanvas(BaseNumberedCanvas):
    footer_row_height = 60


class ManifestReport(Report):

    def __init__(self, stock_transfer: StockTransfer = None, **kwargs):
        self.stock_transfer = stock_transfer
        self.protocol_name = ResearchProtocolConfig().protocol_title
        super().__init__(**kwargs)

    def draw_header(self, canvas, doc):
        width, height = A4
        canvas.setFontSize(6)
        text_width = stringWidth(self.protocol_name, "Helvetica", 6)
        canvas.drawRightString(width - text_width, height - 20, self.protocol_name.upper())
        canvas.drawString(
            40,
            height - 30,
            _("Stock Transfer Manifest: %(transfer_identifier)s").upper()
            % {"transfer_identifier": self.stock_transfer.transfer_identifier},
        )

    def get_report_story(self, **kwargs):
        queryset = self.stock_transfer.stocktransferitem_set.all().order_by(
            "stock__allocation__registered_subject__subject_identifier"
        )
        story = []

        data = [
            [
                Paragraph(
                    _("Stock Transfer Manifest").upper(),
                    ParagraphStyle(
                        "Title",
                        fontSize=10,
                        spaceAfter=0,
                        alignment=TA_LEFT,
                        fontName="Helvetica-Bold",
                    ),
                ),
                Paragraph(
                    self.protocol_name.upper(),
                    ParagraphStyle(
                        "Title",
                        fontSize=10,
                        spaceAfter=0,
                        alignment=TA_RIGHT,
                        fontName="Helvetica-Bold",
                    ),
                ),
            ],
        ]
        table = Table(data)
        story.append(table)
        story.append(Spacer(0.1 * cm, 0.5 * cm))

        left_style = ParagraphStyle(name="line_data_medium", alignment=TA_LEFT, fontSize=10)
        right_style = ParagraphStyle(name="line_data_medium", alignment=TA_RIGHT, fontSize=10)
        from_location = self.stock_transfer.from_location.display_name
        contact_name = self.stock_transfer.from_location.contact_name or ""
        tel = self.stock_transfer.from_location.contact_tel or ""
        email = self.stock_transfer.from_location.contact_email or ""
        timestamp = to_local(self.stock_transfer.transfer_datetime).strftime("%Y-%m-%d")
        data = [
            [
                Paragraph(_("Reference:"), left_style),
                Paragraph(self.stock_transfer.transfer_identifier, left_style),
                Paragraph(_("Contact:"), right_style),
            ],
            [
                Paragraph(_("Date:"), left_style),
                Paragraph(timestamp),
                Paragraph(contact_name, right_style),
            ],
            [
                Paragraph(_("From:"), left_style),
                Paragraph(from_location, left_style),
                Paragraph(email, right_style),
            ],
            [
                Paragraph(_("To:"), left_style),
                Paragraph(self.stock_transfer.to_location.display_name, left_style),
                Paragraph(tel, right_style),
            ],
            [
                Paragraph("", left_style),
                Paragraph("", left_style),
                Paragraph("", right_style),
            ],
        ]
        text_width1 = stringWidth(_("Reference"), "Helvetica", 10)
        table = Table(data, colWidths=(text_width1 * 1.5, None, None))
        story.append(table)

        style = ParagraphStyle(
            name="line_data_medium", alignment=TA_LEFT, fontSize=8, leading=10
        )
        right_style = ParagraphStyle(
            name="line_data_medium", alignment=TA_CENTER, fontSize=8, leading=10
        )
        data = [
            [
                Paragraph(_("%(count)s items") % {"count": queryset.count()}, style),
                Paragraph("_________________________", right_style),
                Paragraph("_________________________", right_style),
                Paragraph("_________________________", right_style),
                Paragraph("__________", right_style),
            ],
            [
                Paragraph("", style),
                Paragraph(_("Issued by: signature /date"), style),
                Paragraph(_("Received by: signature / date"), right_style),
                Paragraph(_("Received by: printed name"), right_style),
                Paragraph(_("Received count"), right_style),
            ],
        ]
        table = Table(data, colWidths=(None, None, None, None, None))
        story.append(table)

        style = ParagraphStyle(name="line_data_medium", alignment=TA_LEFT, fontSize=8)
        data = [
            [
                Paragraph(
                    _(
                        "Place a check mark next to each received item in the left column. "
                        "If there are discrepencies, indicate with a note in the right column."
                    ),
                    style,
                ),
            ],
        ]
        table = Table(data)
        story.append(table)

        style = ParagraphStyle(
            name="line_data_medium",
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.black,
            fontName="Helvetica-Bold",
        )
        data = [
            [
                Paragraph("", style),
                Paragraph("#", style),
                Paragraph(_("Barcode"), style),
                Paragraph(_("Code"), style),
                Paragraph(_("Subject"), style),
                Paragraph(_("Formulation"), style),
                Paragraph(_("Container"), style),
                Paragraph(_("Note"), style),
            ]
        ]
        for index, stock_transfer_item in enumerate(queryset):
            barcode = code128.Code128(
                stock_transfer_item.stock.code, barHeight=6 * mm, barWidth=0.7, gap=1.7
            )
            subject_identifier = (
                stock_transfer_item.stock.allocation.registered_subject.subject_identifier
            )
            formulation = stock_transfer_item.stock.product.formulation
            description = (
                f"{formulation.medication.display_name} "
                f"{int(formulation.strength)}{formulation.units.display_name}"
            )
            style = ParagraphStyle(
                name="line_data", alignment=TA_CENTER, fontSize=8, leading=10
            )
            data.append(
                [
                    Paragraph(" ", style),
                    Paragraph(str(index + 1), style),
                    barcode,
                    Paragraph(stock_transfer_item.stock.code, style),
                    Paragraph(subject_identifier, style),
                    Paragraph(description, style),
                    Paragraph(str(stock_transfer_item.stock.container), style),
                    Paragraph("      ", style),
                ]
            )

        table = Table(
            data,
            colWidths=(0.5 * cm, 1 * cm, 3.5 * cm, None, None, None, None, None),
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(table)

        return story
