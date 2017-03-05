from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.platypus import Paragraph

from django.apps import apps as django_apps
from django.utils import timezone


class Report:

    def __init__(self, header_line=None, **kwargs):
        self._styles = None
        self.edc_base_app_config = django_apps.get_app_config('edc_base')
        self.edc_protocol_app_config = django_apps.get_app_config(
            'edc_protocol')
        self.header_line = header_line or self.edc_base_app_config.institution

    def header_footer(self, canvas, doc):
        canvas.saveState()
        _, height = A4

        header_para = Paragraph(
            self.header_line,
            self.styles['header'])
        header_para.drawOn(canvas, doc.leftMargin, height - 15)

        footer_para = Paragraph(
            'printed on {}'.format(timezone.now().strftime('%Y-%m-%d %H:%M')),
            self.styles['footer'])
        _, h = footer_para.wrap(doc.width, doc.bottomMargin)
        footer_para.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    @property
    def styles(self):
        if not self._styles:
            styles = getSampleStyleSheet()
            styles.add(
                ParagraphStyle(name='header', fontSize=6, alignment=TA_CENTER))
            styles.add(
                ParagraphStyle(name='footer', fontSize=6, alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name='center', alignment=TA_CENTER))
            styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
            styles.add(ParagraphStyle(name='left', alignment=TA_LEFT))
            styles.add(ParagraphStyle(
                name='line_data', alignment=TA_LEFT, fontSize=8, leading=7))
            styles.add(ParagraphStyle(
                name='line_data_small', alignment=TA_LEFT, fontSize=7, leading=8))
            styles.add(ParagraphStyle(
                name='line_data_small_center', alignment=TA_CENTER, fontSize=7, leading=8))
            styles.add(ParagraphStyle(
                name='line_data_large', alignment=TA_LEFT, fontSize=12, leading=12))
            styles.add(ParagraphStyle(
                name='line_data_largest', alignment=TA_LEFT, fontSize=14, leading=15))
            styles.add(ParagraphStyle(
                name='line_label', font='Helvetica-Bold', fontSize=7, leading=6, alignment=TA_LEFT))
            styles.add(ParagraphStyle(
                name='line_label_center',
                font='Helvetica-Bold', fontSize=7, alignment=TA_CENTER))
            styles.add(ParagraphStyle(
                name='row_header',
                font='Helvetica-Bold', fontSize=8, leading=8, alignment=TA_CENTER))
            styles.add(ParagraphStyle(
                name='row_data',
                font='Helvetica', fontSize=7, leading=7, alignment=TA_CENTER,))
            self._styles = styles
        return self._styles
