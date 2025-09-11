from __future__ import annotations

from typing import TYPE_CHECKING

from reportlab.graphics.barcode.widgets import BarcodeCode128
from reportlab.graphics.shapes import Drawing, String

from edc_protocol.research_protocol_config import ResearchProtocolConfig

from ..utils import format_qty
from .draw_label_watermark import draw_label_watermark

if TYPE_CHECKING:
    from ..models import Stock


def draw_patient_stock_label_code128(
    label: Drawing,
    width: int | float,
    height: int | float,
    obj: Stock,
) -> Drawing:
    """Callable to draw a single study medication label given a model
    instance `obj`
    """

    draw_label_watermark(label, width, height)

    br = BarcodeCode128(humanReadable=True, barHeight=30, barWidth=0.7, gap=1.7)
    br.value = obj.code
    br.x = 0
    br.y = height - 40
    label.add(br)

    qty = format_qty(obj.container.qty, obj.container)
    formulation = obj.product.formulation
    product = (
        f"{formulation.medication} {int(formulation.strength)}"
        f"{formulation.get_units_display()} "
    )
    label.add(String(15, height - 72, ResearchProtocolConfig().protocol_name, fontSize=10))
    label.add(String(15, height - 84, f"{product}", fontSize=10))
    label.add(String(15, height - 96, f"{qty} tabs", fontSize=10))
    return label
