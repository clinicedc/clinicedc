from django.db.models import QuerySet, Sum
from django.utils.translation import gettext as _
from edc_pdf_reports import Report
from edc_protocol.research_protocol_config import ResearchProtocolConfig
from reportlab.graphics.barcode import code128
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..models import Stock
from ..utils import get_related_or_none


class StockReport(Report):

    def __init__(self, queryset: QuerySet[Stock] = None, **kwargs):
        self.queryset = queryset.order_by("from_stock__code", "code")
        self.protocol_name = ResearchProtocolConfig().protocol_title
        super().__init__(**kwargs)

    def draw_header(self, canvas, doc):
        width, height = self.page.get("pagesize")
        canvas.setFontSize(6)
        text_width = stringWidth(self.protocol_name, "Helvetica", 6)
        canvas.drawRightString(width - text_width, height - 20, self.protocol_name.upper())
        canvas.drawString(
            40,
            height - 30,
            _("Stock Report").upper(),
        )

    def get_report_story(self, document_template: SimpleDocTemplate = None, **kwargs):
        story = []

        data = [
            [
                Paragraph(
                    _("Stock Report").upper(),
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

        story.append(self.stock_items_as_table)

        story.append(Spacer(0.1 * cm, 0.5 * cm))

        return story

    @property
    def stock_items_as_table(self) -> Table:

        style = ParagraphStyle(
            name="line_data_medium",
            alignment=TA_CENTER,
            fontSize=8,
            textColor=colors.black,
            fontName="Helvetica-Bold",
        )
        data = [
            [
                Paragraph("#", style),
                Paragraph(_("BARCODE"), style),
                Paragraph(_("STOCK"), style),
                Paragraph(_("FROM"), style),
                Paragraph(_("SUBJECT"), style),
                Paragraph(_("FORMULATION"), style),
                Paragraph(_("PACK"), style),
                Paragraph(_("CATSD"), style),
                Paragraph(_("IN"), style),
                Paragraph(_("OUT"), style),
                Paragraph(_("QTY"), style),
            ]
        ]
        for index, stock_obj in enumerate(self.queryset.all()):
            barcode = code128.Code128(stock_obj.code, barHeight=5 * mm, barWidth=0.7, gap=1.7)
            subject_identifier = (
                stock_obj.allocation.registered_subject.subject_identifier
                if stock_obj.allocated
                else ""
            )
            formulation = stock_obj.product.formulation
            description = f"{formulation.imp_description} "
            catsd = self.get_catsbd(stock_obj)
            style = ParagraphStyle(
                name="line_data", alignment=TA_CENTER, fontSize=8, leading=10
            )
            num_style = ParagraphStyle(
                name="line_data", alignment=TA_RIGHT, fontSize=8, leading=10
            )
            style_xsmall = ParagraphStyle(
                name="line_data", alignment=TA_CENTER, fontSize=6, leading=8
            )
            from_stock_code = ""
            if stock_obj.from_stock:
                from_stock_code = stock_obj.from_stock.code
            qty_in = str(int(stock_obj.unit_qty_in))
            qty_out = str(int(stock_obj.unit_qty_out))
            qty = str(int(stock_obj.unit_qty_in - stock_obj.unit_qty_out))
            data.append(
                [
                    Paragraph(str(index + 1), style),
                    barcode,
                    Paragraph(stock_obj.code, style),
                    Paragraph(from_stock_code, style),
                    Paragraph(subject_identifier, style),
                    Paragraph(description, style_xsmall),
                    Paragraph(str(stock_obj.container), style),
                    Paragraph(
                        catsd,
                        ParagraphStyle(
                            name="line_data",
                            alignment=TA_CENTER,
                            fontName="Courier",
                            fontSize=8,
                            leading=10,
                        ),
                    ),
                    Paragraph(qty_in, num_style),
                    Paragraph(qty_out, num_style),
                    Paragraph(qty, num_style),
                ]
            )
        totals = self.queryset.values("unit_qty_in", "unit_qty_out").aggregate(
            Sum("unit_qty_in"), Sum("unit_qty_out")
        )
        tot_qty_in = totals.get("unit_qty_in__sum")
        tot_qty_out = totals.get("unit_qty_out__sum")
        total = tot_qty_in - tot_qty_out
        data.append(
            [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                Paragraph(str(int(tot_qty_in)), num_style),
                Paragraph(str(int(tot_qty_out)), num_style),
                Paragraph(str(int(total)), num_style),
            ]
        )

        table = Table(
            data,
            colWidths=(1 * cm, None, None, None, None, None, None, None, None, None, None),
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

    @staticmethod
    def get_catsbd(stock_obj: Stock) -> str:
        catsd = ""
        catsd += "C" if get_related_or_none(stock_obj, "stock_obj.confirmed") else "-"
        catsd += "A" if get_related_or_none(stock_obj, "allocation") else "-"
        catsd += "T" if get_related_or_none(stock_obj, "stocktransferitem") else "-"
        catsd += "S" if get_related_or_none(stock_obj, "confirmationatsiteitem") else "-"
        catsd += "B" if get_related_or_none(stock_obj, "stored_at_site else") else "-"
        catsd += "D" if get_related_or_none(stock_obj, "dispense") else "-"
        return catsd
