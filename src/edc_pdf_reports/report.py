from __future__ import annotations

import os.path
import sys
import warnings
from abc import ABC
from io import BytesIO
from uuid import uuid4

from django.contrib import messages
from django.http import HttpResponse
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
from reportlab.platypus import Paragraph, SimpleDocTemplate

from .numbered_canvas import NumberedCanvas


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

    def __init__(self, page=None, header_line=None, filename=None, request=None, **kwargs):
        self._styles = None
        self.request = request
        self.page = page or self.default_page

        self.report_filename = filename or f"{uuid4()}.pdf"

        if not header_line:
            header_line = Protocol().institution
        self.header_line = header_line

    def get_report_story(self, **kwargs):
        return []

    def draw_footer(self, canvas, doc):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="header", fontSize=6, alignment=TA_CENTER))
        width, _ = A4
        canvas.setFontSize(6)
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        canvas.drawRightString(width - len(timestamp) - 20, 25, f"printed on {timestamp}")
        canvas.drawString(35, 25, f"clinicedc {Revision().tag}")

    def on_first_page(self, canvas, doc):
        """Callback for `onFirstPage`"""
        self.draw_footer(canvas, doc)

    def on_later_pages(self, canvas, doc):
        """Callback for onLaterPages"""
        self.draw_footer(canvas, doc)

    def render_to_buffer(self, **kwargs):
        buffer = BytesIO()
        document_template = self.document_template(buffer, **self.page)
        story = self.get_report_story(**kwargs)
        document_template.build(
            story,
            onFirstPage=self.on_first_page,
            onLaterPages=self.on_later_pages,
            canvasmaker=NumberedCanvas,
        )
        buffer_value = buffer.getvalue()
        buffer.close()
        return buffer_value

    def render(self, message_user: bool | None = None, **kwargs):
        """Deprecated wrapper for render_to_response"""
        warnings.warn(
            "Method `render` has been deprecated. Use `render_to_response` instead.",
            DeprecationWarning,
        )
        return self.render_to_response(message_user=message_user, **kwargs)

    def render_to_response(self, message_user: bool | None = None, **kwargs):
        """Render buffer to HTTP response"""
        message_user = True if message_user is None else message_user
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{self.report_filename}"'
        buffer_value = self.render_to_buffer()
        response.write(buffer_value)
        if message_user and self.request:
            self.message_user(**kwargs)
        return response

    def render_to_file(self, path: str, verbose: bool | None = None):
        """Render buffer to file"""
        buffer_value = self.render_to_buffer()
        if not os.path.exists(path):
            raise ReportError(f"Path does not exist. Got {path}")
        else:
            filename = os.path.join(path, self.report_filename)
            with open(filename, "wb") as f:
                f.write(buffer_value)
                if verbose:
                    sys.stdout.write(f"Created file {filename}\n")
        return None

    def message_user(self, **kwargs):
        messages.success(
            self.request,
            f"The report has been exported as a PDF. See downloads in your browser. "
            f"The filename is '{self.report_filename}'.",
            fail_silently=True,
        )

    def header_footer(self, canvas, doc):
        canvas.saveState()
        _, height = A4

        header_para = Paragraph(self.header_line, self.styles["header"])
        header_para.drawOn(canvas, doc.leftMargin, height - 15)

        dte = timezone.now().strftime("%Y-%m-%d %H:%M")
        footer_para = Paragraph(f"printed on {dte}", self.styles["footer"])
        _, h = footer_para.wrap(doc.width, doc.bottomMargin)
        footer_para.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

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
