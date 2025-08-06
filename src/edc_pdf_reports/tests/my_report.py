from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tables import Table, TableStyle

from edc_pdf_reports import Report

dummy_text = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer at purus eros.
Aliquam erat volutpat. Donec sollicitudin tempor tellus, vitae tincidunt ipsum
mattis quis. Nulla bibendum molestie rutrum. Proin nec erat quis leo posuere posuere.
Phasellus cursus leo non mauris tristique, at imperdiet enim pharetra. Morbi vel
massa neque. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere
cubilia Curae; Maecenas id dignissim ipsum.

Phasellus aliquam suscipit enim in elementum. Nam vehicula, enim quis mattis porttitor,
lacus nulla placerat lectus, et volutpat metus lorem maximus dui. In vel mollis nisl.
Vestibulum volutpat nulla quam, vel mollis velit pulvinar et. Ut fringilla odio nec
libero efficitur tempus. Fusce laoreet iaculis velit in sagittis. Donec metus massa,
condimentum ac mauris tempus, dignissim luctus eros.
"""


class MyReport(Report):
    def get_report_story(self, **kwargs):
        story = []
        data = [[Paragraph(dummy_text, self.styles["line_data_large"])]]

        t = Table(data, colWidths=(9 * cm))
        t.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (0, 1), 0.25, colors.black),
                    ("INNERGRID", (0, 2), (0, 3), 0.25, colors.black),
                ]
            )
        )
        t.hAlign = "RIGHT"

        story.append(t)
        return story
