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

from ..models import ReturnRequest


class ReturnNumberedCanvas(BaseNumberedCanvas):
    footer_row_height = 60


class ReturnManifestReport(Report):
    def __init__(self, return_request: ReturnRequest = None, **kwargs):
        self.return_request = return_request
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
                _("Stock Return Manifest: %(return_identifier)s")
                % {"return_identifier": self.return_request.return_identifier}
            ).upper(),
        )

    @property
    def queryset(self):
        return self.return_request.returnitem_set.all().order_by("code")

    def get_report_story(self, document_template: SimpleDocTemplate = None, **kwargs):  # noqa: ARG002
        story = []

        data = [
            [
                Paragraph(
                    _("Stock Return Manifest").upper(),
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
            name="bold_left",
            alignment=TA_LEFT,
            fontSize=8,
            fontName="Helvetica-Bold",
        )
        bold_right_style = ParagraphStyle(
            name="bold_right",
            alignment=TA_RIGHT,
            fontSize=8,
            fontName="Helvetica-Bold",
        )
        left_style = ParagraphStyle(name="left", alignment=TA_LEFT, fontSize=8)
        right_style = ParagraphStyle(name="right", alignment=TA_RIGHT, fontSize=8)

        from_location = self.return_request.from_location.display_name
        contact_name = self.return_request.from_location.contact_name or ""
        tel = self.return_request.from_location.contact_tel or ""
        email = self.return_request.from_location.contact_email or ""
        timestamp = to_local(self.return_request.return_datetime).strftime("%Y-%m-%d")

        data = [
            [
                Paragraph(_("Reference:"), bold_left_style),
                Paragraph(self.return_request.return_identifier, left_style),
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
                Paragraph(self.return_request.to_location.display_name, left_style),
                Paragraph(tel, right_style),
            ],
            [
                Paragraph(_("Items:"), bold_left_style),
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

        story.append(self.return_items_as_table)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        story.append(self.signature_line_as_table)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        story.append(self.comment_box_as_table)

        return story

    @property
    def return_items_as_table(self) -> Table:
        header_style = ParagraphStyle(
            name="header",
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.black,
            fontName="Helvetica-Bold",
        )
        data = [
            [
                Paragraph("", header_style),
                Paragraph("#", header_style),
                Paragraph(_("Subject"), header_style),
                Paragraph(_("Code"), header_style),
                Paragraph(_("Barcode"), header_style),
                Paragraph(_("Formulation"), header_style),
                Paragraph(_("Pack"), header_style),
            ]
        ]
        for index, return_item in enumerate(self.queryset):
            stock = return_item.stock
            barcode = code128.Code128(
                stock.code, barHeight=5 * mm, barWidth=0.7, gap=1.7
            )
            formulation = stock.product.formulation
            description = f"{formulation.imp_description} "
            cell_style = ParagraphStyle(
                name="cell", alignment=TA_CENTER, fontSize=8, leading=10
            )
            cell_style_xsmall = ParagraphStyle(
                name="cell_xsmall", alignment=TA_CENTER, fontSize=6, leading=8
            )
            # allocation is set while the stock is in transit or held
            # at central awaiting disposition. If the manifest is printed after
            # disposition, fall back to the most recent historical allocation.
            allocation = stock.allocation or (
                stock.allocations
                .select_related("registered_subject")
                .order_by("-started_datetime")
                .first()
            )
            subject_identifier = (
                allocation.registered_subject.subject_identifier
                if allocation else "-"
            )
            data.append(
                [
                    CheckboxFlowable(name=f"checkbox_{index}"),
                    Paragraph(str(index + 1), cell_style),
                    Paragraph(subject_identifier, cell_style),
                    Paragraph(
                        f"{stock.code[:3]}-{stock.code[3:]}",
                        cell_style,
                    ),
                    barcode,
                    Paragraph(description, cell_style_xsmall),
                    Paragraph(str(stock.container), cell_style),
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
            name="sig_label", alignment=TA_LEFT, fontSize=8, leading=8
        )
        textfield_width = stringWidth("_________________________", "Helvetica", 8)
        data = [
            [
                TextFieldFlowable(
                    name="dispatched_by_signature",
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
                    name="received_by_name",
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
                Paragraph(_("Dispatched by: signature / date"), style=style),
                Paragraph(_("Received by: signature / date"), style=style),
                Paragraph(_("Received by: printed name"), style=style),
                Paragraph(_("Received count"), style=style),
            ],
        ]
        return Table(data, colWidths=(None, None, None, None), rowHeights=(10, 10))

    @property
    def comment_box_as_table(self) -> Table:
        style = ParagraphStyle(
            name="comment_header",
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
