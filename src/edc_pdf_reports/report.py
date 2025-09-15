from __future__ import annotations

from abc import ABC
from uuid import uuid4

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django_revision.revision import Revision
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate

from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils.date import to_local

from .numbered_canvas import NumberedCanvas


class ReportError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class Report(ABC):
    document_template = SimpleDocTemplate
    watermark_word: str | None = getattr(settings, "EDC_PDF_REPORTS_WATERMARK_WORD", None)
    watermark_font: tuple[str, int] | None = getattr(
        settings, "EDC_PDF_REPORTS_WATERMARK_FONT", ("Helvetica", 100)
    )
    default_numbered_canvas = NumberedCanvas

    default_page = dict(
        rightMargin=0.5 * cm,
        leftMargin=0.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        pagesize=A4,
    )

    def __init__(
        self,
        page: dict | None = None,
        header_line: str | None = None,
        filename: str | None = None,
        request: WSGIRequest | None = None,
        numbered_canvas: type[NumberedCanvas] | None = None,
        footer_row_height: int | None = None,
    ):
        self._styles = None
        self.request = request
        self.page = page or self.default_page
        self.filename = filename or f"{uuid4()}.pdf"
        self.footer_row_height = footer_row_height or 25
        self.numbered_canvas = numbered_canvas or self.default_numbered_canvas

        if not header_line:
            header_line = ResearchProtocolConfig().institution
        self.header_line = header_line

    def build(self, response):
        document_template = self.document_template(response, **self.page)
        story = self.get_report_story(document_template=document_template)  # flowables
        document_template.build(
            story,
            onFirstPage=self.on_first_page,
            onLaterPages=self.on_later_pages,
            canvasmaker=self.numbered_canvas,
        )

    @property
    def numbered_canvas(self):
        return self._numbered_canvas

    @numbered_canvas.setter
    def numbered_canvas(self, value: type[NumberedCanvas]):
        self._numbered_canvas = value
        if self.watermark_word:
            self._numbered_canvas.watermark_word = self.watermark_word
            if self.watermark_font:
                self._numbered_canvas.watermark_font = self.watermark_font

    @property
    def report_filename(self) -> str:
        return self.filename

    def get_report_story(self, **kwargs):
        """Entry point, returns a list of flowables to be passed to build.

        For example, where ``pdf_report`` is an instance of this class:

            buffer = BytesIO()
            doctemplate = pdf_report.document_template(buffer, **pdf_report.page)
            story = pdf_report.get_report_story()
            doctemplate.build(
                story,
                onFirstPage=pdf_report.on_first_page,
                onLaterPages=pdf_report.on_later_pages,
                canvasmaker=NumberedCanvas)
            buffer.seek(0)

        """
        return []

    def on_first_page(self, canvas, doc):
        """Callback for `onFirstPage`"""
        self.draw_footer(canvas, doc)

    def on_later_pages(self, canvas, doc):
        """Callback for onLaterPages"""
        self.draw_header(canvas, doc)
        self.draw_footer(canvas, doc)

    def draw_header(self, canvas, doc):
        pass

    def draw_footer(self, canvas, doc):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="header", fontSize=6, alignment=TA_CENTER))
        width, _ = A4
        canvas.setFontSize(6)
        timestamp = to_local(timezone.now()).strftime("%Y-%m-%d %H:%M")
        canvas.drawRightString(
            width - len(timestamp) - 20,
            self.footer_row_height,
            f"printed on {timestamp}",
        )
        canvas.drawString(35, self.footer_row_height, f"clinicedc {Revision().tag}")

    @property
    def styles(self):
        if not self._styles:
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name="titleR", fontSize=8, alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name="header", fontSize=6, alignment=TA_CENTER))
            styles.add(ParagraphStyle(name="footer", fontSize=6, alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name="center", alignment=TA_CENTER))
            styles.add(ParagraphStyle(name="right", alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name="left", alignment=TA_LEFT))
            styles.add(
                ParagraphStyle(name="line_data", alignment=TA_LEFT, fontSize=8, leading=10)
            )
            styles.add(
                ParagraphStyle(
                    name="line_data_small", alignment=TA_LEFT, fontSize=7, leading=9
                )
            )
            styles.add(
                ParagraphStyle(
                    name="line_data_small_center",
                    alignment=TA_CENTER,
                    fontSize=7,
                    leading=8,
                )
            )
            styles.add(
                ParagraphStyle(
                    name="line_data_medium", alignment=TA_LEFT, fontSize=10, leading=12
                )
            )
            styles.add(
                ParagraphStyle(
                    name="line_data_mediumB",
                    alignment=TA_LEFT,
                    fontSize=10,
                    leading=11,
                    fontName="Helvetica-Bold",
                )
            )
            styles.add(
                ParagraphStyle(
                    name="line_data_large", alignment=TA_LEFT, fontSize=11, leading=14
                )
            )
            styles.add(
                ParagraphStyle(
                    name="line_data_largest", alignment=TA_LEFT, fontSize=14, leading=18
                )
            )
            styles.add(
                ParagraphStyle(name="line_label", fontSize=7, leading=6, alignment=TA_LEFT)
            )
            styles.add(
                ParagraphStyle(name="line_label_center", fontSize=7, alignment=TA_CENTER)
            )
            styles.add(
                ParagraphStyle(name="row_header", fontSize=8, leading=8, alignment=TA_CENTER)
            )
            styles.add(
                ParagraphStyle(name="row_data", fontSize=7, leading=7, alignment=TA_CENTER)
            )
            self._styles = self.add_to_styles(styles)
        return self._styles

    def add_to_styles(self, styles: StyleSheet1) -> StyleSheet1:
        return styles
