from reportlab.graphics.barcode.widgets import BarcodeStandard39
from reportlab.graphics.shapes import Drawing, String

from edc_protocol.research_protocol_config import ResearchProtocolConfig

from ..models import Stock
from ..utils import format_qty


def draw_bulk_stock_label_code39(
    label: Drawing,
    width: int | float,
    height: int | float,
    obj: Stock,
) -> Drawing:
    """Callable to draw a single study medication label given a model
    instance `obj`
    """
    br = BarcodeStandard39(
        humanReadable=True, checksum=False, barHeight=30, barWidth=0.7, gap=1.7
    )
    br.value = obj.code
    br.x = width - 100
    br.y = height - 40
    label.add(br)
    label.add(String(15, height - 20, ResearchProtocolConfig().protocol_name, fontSize=10))
    qty = format_qty(obj.container.qty, obj.container)

    label.add(String(15, height - 40, f"{qty} tabs", fontSize=10))
    label.add(String(15, height - 60, f"Lot: {obj.lot.lot_no}", fontSize=10))
    label.add(String(15, height - 80, f"Expires: {obj.lot.expiration_date}", fontSize=10))
    product = obj.product.formulation.get_description_with_assignment(obj.product.assignment)
    label.add(String(15, height - 100, f"{product}", fontSize=10))
    return label
