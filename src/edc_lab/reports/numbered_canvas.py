from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from django.utils import timezone
from django_revision.revision import Revision


class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(name='header', fontSize=6, alignment=TA_CENTER))
        width, _ = A4
        self.setFont('Helvetica', 6)
        self.drawCentredString(
            width / 2, 25, "Page %d of %d" % (self.getPageNumber(), page_count))
        timestamp = 'printed on {}'.format(
            timezone.now().strftime('%Y-%m-%d %H:%M'))
        self.drawRightString(
            width - len(timestamp), 25, 'printed on {}'.format(timezone.now().strftime('%Y-%m-%d %H:%M')))
        self.drawString(15, 25, 'revision {}'.format(Revision().revision))
