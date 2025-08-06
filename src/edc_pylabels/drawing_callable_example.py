from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.sites.models import Site
from reportlab.graphics.barcode.widgets import BarcodeStandard39
from reportlab.graphics.charts.textlabels import Label as RlLabel
from reportlab.graphics.shapes import Drawing, String

if TYPE_CHECKING:
    # you may also refer to models in clinicedc/edc-pharmacy
    class Container:
        qty: int

    class Request:
        container: Container

    class RequestItem:
        subject_identifier: str
        code: str
        gender: str
        sid: int | str
        site: Site
        request: Request


def draw_callable_example(
    label: Drawing,
    width: int | float,
    height: int | float,
    obj: RequestItem,
) -> Drawing:
    """Callable to draw a single study medication label given a model
    instance `obj`

    Prints a code39 barcode for the code attribute of obj.
    """
    br = BarcodeStandard39(
        humanReadable=True, checksum=False, barHeight=30, barWidth=0.7, gap=1.7
    )
    br.value = obj.code
    br.x = width - 140
    br.y = 25
    label.add(br)
    label.add(String(15, height - 20, f"TEST!! Study - {obj.site.name.title()}", fontSize=10))
    label.add(
        String(
            width - 110,
            height - 40,
            f"{obj.subject_identifier}{obj.gender}",
            fontSize=12,
        )
    )
    label.add(String(15, height - 40, "Medication for the research", fontSize=10))
    label.add(String(15, height - 50, "trial TEST!!.", fontSize=10))
    label.add(String(15, height - 70, "Take 4 pills only at night.", fontSize=10))
    label.add(String(15, 20, f"{obj.request.container.qty} tabs", fontSize=10))
    lab = RlLabel(x=width - 20, y=40, fontSize=10, angle=90)
    lab.setText(str(obj.sid))
    label.add(lab)
    return label
