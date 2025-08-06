from django.conf import settings
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    static_footer_text = None
    footer_row_height = 25
    watermark_word: str | None = getattr(settings, "EDC_PHARMACY_WATERMARK_WORD", None)
    watermark_font: tuple[str, int] = getattr(
        settings, "EDC_PHARMACY_WATERMARK_FONT", ("Helvetica", 100)
    )
    pagsize = A4

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
            if self.watermark_word:
                self.draw_watermark()
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="header", fontSize=6, alignment=TA_CENTER))
        width, _ = self.pagsize
        self.setFont("Helvetica", 6)
        self.drawCentredString(
            width / 2,
            self.footer_row_height,
            "Page %d of %d" % (self.getPageNumber(), page_count),
        )

    def draw_watermark(self):
        self.saveState()
        width, height = self.pagsize
        self.setFont(*self.watermark_font)
        self.setFillGray(0.5, 0.5)  # Light gray color
        self.translate(width / 2, height / 2)
        self.rotate(45)
        self.drawCentredString(0, 0, self.watermark_word)
        self.restoreState()
