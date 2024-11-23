from django.conf import settings
from reportlab.graphics.shapes import Group, String
from reportlab.lib import colors


def draw_label_watermark(label, width, height, **string_options):
    if word := getattr(settings, "EDC_PHARMACY_LABEL_WATERMARK_WORD", None):
        string_opts = dict(
            fontName="Helvetica",
            fontSize=28,
            textAnchor="middle",
            fillColor=colors.Color(0.5, 0.5, 0.5, alpha=0.7),
        )
        string_opts.update(string_options)
        text_group = Group()
        watermark = String(height / 2, 10, word, **string_opts)
        text_group.add(watermark)
        text_group.translate(width / 3, height - height * 0.95)
        text_group.rotate(45)
        label.add(text_group)
