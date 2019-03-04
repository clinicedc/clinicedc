from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from edc_lab.constants import SHIPPED
from edc_lab.models import BoxItem

register = template.Library()


@register.inclusion_tag(
    f"edc_lab_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/"
    f"listboard/box/box_cell.html"
)
def show_box_rows(box, listboard_url, position=None):
    """Returns rendered HTML of a box as a dictionary of keys headers, rows.

    Usage::

        {% block results_body %}
            {% show_box_rows box listboard_url position=position %}
        {% endblock results_body %}

    """
    position = "0" if position is None else str(position)
    btn_style = {-1: "btn-danger", 0: "btn-default", 1: "btn-success"}
    pos = 0
    rows = []
    header = range(1, box.box_type.across + 1)
    for i in range(1, box.box_type.down + 1):
        row = {}
        row["position"] = i
        row["cells"] = []
        for _ in range(1, box.box_type.across + 1):
            cell = {}
            pos += 1
            try:
                box_item = box.boxitem_set.get(position=pos)
            except ObjectDoesNotExist:
                box_item = BoxItem(box=box)
            cell["btn_style"] = btn_style.get(box_item.verified)
            cell["btn_label"] = str(pos).zfill(2)
            cell["btn_title"] = box_item.human_readable_identifier or "empty"
            cell["has_focus"] = str(pos) == position
            cell["box_item"] = box_item
            row["cells"].append(cell)
        rows.append(row)
    return {"headers": header, "rows": rows}


@register.filter(is_safe=True)
def verified(box_item):
    """Returns a safe HTML check mark string if a Box item has been verified.
    """
    verified = False
    if box_item.verified:
        if int(box_item.verified) == 1:
            verified = True
        elif int(box_item.verified) == -1:
            verified = False
    return (
        ""
        if not verified
        else mark_safe(
            '&nbsp;<span title="verified" alt="verified" class="text text-success">'
            '<i class="fas fa-check fa-fw"></i></span>'
        )
    )


@register.filter(is_safe=True)
def shipped(box_item):
    """Returns a safe HTML check mark string if a Box item has been shipped.
    """
    return (
        ""
        if not box_item.status == SHIPPED
        else mark_safe(
            '&nbsp;<span title="shipped" class="text text-success">'
            '<i class="fas fa-ship fa-fw"></i></span>'
        )
    )


@register.inclusion_tag(
    f"edc_lab_dashboard/bootstrap{settings.EDC_BOOTSTRAP}/"
    "listboard/tags/status_column.html"
)
def status_column(model_wrapper, *attrs):
    options = {}
    for attr in attrs:
        try:
            options.update({attr: True if getattr(model_wrapper, attr) else False})
        except AttributeError:
            pass
    return dict(options=options)
