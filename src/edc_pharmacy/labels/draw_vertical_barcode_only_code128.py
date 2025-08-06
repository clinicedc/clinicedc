from __future__ import annotations

from typing import TYPE_CHECKING

from reportlab.graphics.barcode.widgets import BarcodeCode128
from reportlab.graphics.shapes import Drawing, Group, String
from reportlab.pdfbase.pdfmetrics import stringWidth

from edc_protocol.research_protocol_config import ResearchProtocolConfig

from ..utils import format_qty
from .draw_label_watermark import draw_label_watermark

if TYPE_CHECKING:
    from ..models import Stock


def draw_vertical_barcode_only_code128(
    label: Drawing,
    width: int | float,
    height: int | float,
    obj: Stock,
) -> Drawing:

    draw_label_watermark(label, width, height)

    br = BarcodeCode128(humanReadable=True, barHeight=30, barWidth=0.7, gap=1.7)
    br.value = obj.code
    br.x = 0
    br.y = height - 68
    group = Group()
    group.add(br)
    group.translate(width - 170, height - 108)
    group.rotate(90)
    label.add(group)

    protocol_name = String(0, 0, str(ResearchProtocolConfig().protocol_name))
    qty_text = f"{format_qty(obj.container.qty, obj.container)} tabs"

    text_group = Group()
    text_group.add(protocol_name)

    text_width = stringWidth(qty_text, "Helvetica", 10)
    text_string = String(height - text_width - 10, 0, qty_text)
    text_group.add(text_string)

    text_group.translate(10, height - 100)
    text_group.rotate(90)
    label.add(text_group)

    return label
