from __future__ import annotations

from typing import TYPE_CHECKING

from reportlab.graphics.barcode.widgets import BarcodeStandard39
from reportlab.graphics.charts.textlabels import Label as RlLabel
from reportlab.graphics.shapes import Drawing, String

if TYPE_CHECKING:
    from ..models import RequestItem


def draw_label_with_code39(
    label: Drawing,
    width: int | float,
    height: int | float,
    obj: RequestItem,
) -> Drawing:
    """Callable to draw a single study medication label given a model
    instance `obj`
    """
    br = BarcodeStandard39(
        humanReadable=True, checksum=False, barHeight=30, barWidth=0.7, gap=1.7
    )
    br.value = obj.code
    br.x = width - 140
    br.y = 25
    label.add(br)
    label.add(
        String(15, height - 20, f"META III Study - {obj.site.name.title()}", fontSize=10)
    )
    label.add(
        String(
            width - 110,
            height - 40,
            f"{obj.subject_identifier}{obj.gender}",
            fontSize=12,
        )
    )
    label.add(String(15, height - 40, "Dawa kwa ajili ya utafiti", fontSize=10))
    label.add(String(15, height - 50, "wa META III.", fontSize=10))
    label.add(String(15, height - 70, "Meza vidonge vinne usiku tu.", fontSize=10))
    label.add(String(15, 20, f"{obj.request.container.qty} tabs", fontSize=10))
    lab = RlLabel(x=width - 20, y=40, fontSize=10, angle=90)
    lab.setText(str(obj.sid))
    label.add(lab)
    return label
