from __future__ import annotations

from abc import ABC
from uuid import uuid4

from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django_revision.revision import Revision
from edc_protocol import Protocol
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    StyleSheet1,
    _baseFontNameB,
    getSampleStyleSheet,
)
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate


class ReportError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class Report(ABC):
    document_template = SimpleDocTemplate

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
    ):
        self._styles = None
        self.request = request
        self.page = page or self.default_page

        self.filename = filename or f"{uuid4()}.pdf"

        if not header_line:
            header_line = Protocol().institution
        self.header_line = header_line

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
        self.draw_footer(canvas, doc)

    def draw_footer(self, canvas, doc):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="header", fontSize=6, alignment=TA_CENTER))
        width, _ = A4
        canvas.setFontSize(6)
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        canvas.drawRightString(width - len(timestamp) - 20, 25, f"printed on {timestamp}")
        canvas.drawString(35, 25, f"clinicedc {Revision().tag}")

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
                    fontName=_baseFontNameB,
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
