from django.utils.translation import gettext as _
from reportlab.graphics.barcode import code128
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from edc_pdf_reports import NumberedCanvas as BaseNumberedCanvas
from edc_pdf_reports import Report
from edc_pdf_reports.flowables import CheckboxFlowable, TextFieldFlowable
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils.date import to_local

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
            (
                _("Stock Transfer Manifest: %(transfer_identifier)s")
                % {"transfer_identifier": self.stock_transfer.transfer_identifier}
            ).upper(),
        )

    @property
    def queryset(self):
        return self.stock_transfer.stocktransferitem_set.all().order_by(
            "stock__allocation__registered_subject__subject_identifier"
        )

    def get_report_story(self, document_template: SimpleDocTemplate = None, **kwargs):
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

        bold_left_style = ParagraphStyle(
            name="line_data_medium",
            alignment=TA_LEFT,
            fontSize=8,
            fontName="Helvetica-Bold",
        )
        bold_right_style = ParagraphStyle(
            name="line_data_medium",
            alignment=TA_RIGHT,
            fontSize=8,
            fontName="Helvetica-Bold",
        )
        left_style = ParagraphStyle(name="line_data_medium", alignment=TA_LEFT, fontSize=8)
        right_style = ParagraphStyle(name="line_data_medium", alignment=TA_RIGHT, fontSize=8)
        from_location = self.stock_transfer.from_location.display_name
        contact_name = self.stock_transfer.from_location.contact_name or ""
        tel = self.stock_transfer.from_location.contact_tel or ""
        email = self.stock_transfer.from_location.contact_email or ""
        timestamp = to_local(self.stock_transfer.transfer_datetime).strftime("%Y-%m-%d")
        data = [
            [
                Paragraph(_("Reference:"), bold_left_style),
                Paragraph(self.stock_transfer.transfer_identifier, left_style),
                Paragraph(_("Contact:"), bold_right_style),
            ],
            [
                Paragraph(_("Date:"), bold_left_style),
                Paragraph(timestamp, left_style),
                Paragraph(contact_name, right_style),
            ],
            [
                Paragraph(_("From:"), bold_left_style),
                Paragraph(from_location, left_style),
                Paragraph(email, right_style),
            ],
            [
                Paragraph(_("To:"), bold_left_style),
                Paragraph(self.stock_transfer.to_location.display_name, left_style),
                Paragraph(tel, right_style),
            ],
            [
                Paragraph("Items:", bold_left_style),
                Paragraph(str(self.queryset.count()), left_style),
                Paragraph("", right_style),
            ],
        ]
        text_width1 = stringWidth(_("Reference"), "Helvetica", 10)
        table = Table(
            data,
            colWidths=(text_width1 * 1.5, None, None),
            rowHeights=(10, 10, 10, 10, 10),
        )
        story.append(table)

        story.append(self.stock_transfer_items_as_table)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        story.append(self.signature_line_as_table)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        story.append(self.comment_box_as_table)

        return story

    @property
    def stock_transfer_items_as_table(self) -> Table:

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
                Paragraph(_("Subject"), style),
                Paragraph(_("Code"), style),
                Paragraph(_("Barcode"), style),
                Paragraph(_("Formulation"), style),
                Paragraph(_("Pack"), style),
            ]
        ]
        for index, stock_transfer_item in enumerate(self.queryset):
            barcode = code128.Code128(
                stock_transfer_item.stock.code, barHeight=5 * mm, barWidth=0.7, gap=1.7
            )
            subject_identifier = (
                stock_transfer_item.stock.allocation.registered_subject.subject_identifier
            )
            formulation = stock_transfer_item.stock.product.formulation
            description = f"{formulation.imp_description} "
            style = ParagraphStyle(
                name="line_data", alignment=TA_CENTER, fontSize=8, leading=10
            )
            style_xsmall = ParagraphStyle(
                name="line_data", alignment=TA_CENTER, fontSize=6, leading=8
            )
            data.append(
                [
                    CheckboxFlowable(name=f"checkbox_{index}"),
                    Paragraph(str(index + 1), style),
                    Paragraph(subject_identifier, style),
                    Paragraph(
                        (
                            f"{stock_transfer_item.stock.code[:3]}-"
                            f"{stock_transfer_item.stock.code[3:]}"
                        ),
                        style,
                    ),
                    barcode,
                    Paragraph(description, style_xsmall),
                    Paragraph(str(stock_transfer_item.stock.container), style),
                ]
            )

        table = Table(
            data,
            colWidths=(0.5 * cm, 1 * cm, None, None, None, None, None),
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
        return table

    @property
    def signature_line_as_table(self) -> Table:
        style = ParagraphStyle(
            name="line_data_medium", alignment=TA_LEFT, fontSize=8, leading=8
        )
        textfield_width = stringWidth("_________________________", "Helvetica", 8)
        data = [
            [
                TextFieldFlowable(
                    name="issued_by_signature",
                    value="",
                    width=textfield_width,
                    height=10,
                    borderWidth=0.5,
                    fontSize=8,
                ),
                TextFieldFlowable(
                    name="received_by_signature",
                    value="",
                    width=textfield_width,
                    height=10,
                    borderWidth=0.5,
                    fontSize=8,
                ),
                TextFieldFlowable(
                    name="received_by",
                    value="",
                    width=textfield_width,
                    height=10,
                    borderWidth=0.5,
                    fontSize=8,
                ),
                TextFieldFlowable(
                    name="received_count",
                    value="",
                    width=textfield_width / 2,
                    height=10,
                    borderWidth=0.5,
                    fontSize=8,
                ),
            ],
            [
                Paragraph(_("Issued by: signature /date"), style=style),
                Paragraph(_("Received by: signature / date"), style=style),
                Paragraph(_("Received by: printed name"), style=style),
                Paragraph(_("Received count"), style=style),
            ],
        ]
        table = Table(data, colWidths=(None, None, None, None), rowHeights=(10, 10))
        return table

    @property
    def comment_box_as_table(self) -> Table:
        style = ParagraphStyle(
            name="line_data_medium",
            fontSize=8,
            textColor=colors.black,
            fontName="Helvetica-Bold",
        )
        data = [[Paragraph(_("Comment:"), style)]]
        table = Table(data, rowHeights=(75,))
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
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        return table
