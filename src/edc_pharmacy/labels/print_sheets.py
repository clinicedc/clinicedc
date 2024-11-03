import os.path
from pathlib import Path

from edc_sites.site import sites
from meta_pharmacy.models import LabelData
from pylabels import Sheet, Specification
from reportlab.graphics.barcode.widgets import BarcodeStandard39
from reportlab.graphics.charts.textlabels import Label as RlLabel
from reportlab.graphics.shapes import String


class Label:
    """
    this should be based on a generated dataset using the stock transfer
    request data.

    maybe include a printout for the site to review the IN-STOCK vs ORDER
    status for each subject in a stock transfer request

    subject1 IN-STOCK
    subject2 ORDER
    subject3 ORDER
    """

    def __init__(self, obj: LabelData):
        self.label = obj
        self.gender = obj.gender
        self.site_id = obj.site_id
        self.subject_identifier = obj.subject_identifier
        self.reference = obj.reference
        self.sid = obj.sid
        self.site_name = sites.get(self.site_id).title


def draw_label(label, width, height, data: LabelData):
    data = Label(data)
    br = BarcodeStandard39(
        humanReadable=True, checksum=False, barHeight=30, barWidth=0.7, gap=1.7
    )
    br.value = data.reference
    br.x = width - 140
    br.y = 25
    label.add(br)
    label.add(String(15, height - 20, f"META III Study - {data.site_name}", fontSize=10))
    label.add(
        String(
            width - 120, height - 40, f"{data.subject_identifier}{data.gender}", fontSize=12
        )
    )
    label.add(String(15, height - 40, "Dawa kwa ajili ya utafiti", fontSize=10))
    label.add(String(15, height - 50, "wa META III.", fontSize=10))
    label.add(String(15, height - 70, "Meza vidonge vinne usiku tu.", fontSize=10))
    label.add(String(15, 20, "128 tabs", fontSize=10))
    lab = RlLabel(x=width - 20, y=40, fontSize=10, angle=90)
    # lab.boxAnchor = "ne"
    # lab.dx = 0
    # lab.dy = -20
    lab.setText(data.sid)
    label.add(lab)
    return label


def print_sheets(labels: list[Label], path: Path | None = None, verbose: bool | None = None):
    specs = Specification(
        210,
        297,
        2,
        6,
        96,
        42,
        corner_radius=0,
        top_margin=21,
        left_margin=8,
        right_margin=8,
        bottom_margin=22,
        left_padding=2,
        right_padding=2,
        top_padding=2,
        bottom_padding=2,
    )

    if not path:
        path = Path(os.path.dirname(__file__))
    path = str(path / "meta_labels.pdf")
    sheet = Sheet(specs, draw_label, border=True)

    sheet.add_labels(labels)

    # Save the file and we are done.
    sheet.save(path)
    msg = "{0:d} label(s) output on {1:d} page(s) to {2}.".format(
        sheet.label_count, sheet.page_count, path
    )
    if verbose:
        print(msg)
    return msg
