from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from ..models import BoxItem
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('edc_lab/listboard/box/box_cell.html')
def show_box_rows(box, listboard_url_name, position=None):
    position = '0' if position is None else str(position)
    btn_style = {
        -1: 'btn-danger',
        0: 'btn-default',
        1: 'btn-success'}
    pos = 0
    rows = []
    header = range(1, box.box_type.across + 1)
    for i in range(1, box.box_type.down + 1):
        row = {}
        reverse_kwargs = {}
        row['position'] = i
        row['cells'] = []
        for _ in range(1, box.box_type.across + 1):
            cell = {}
            pos += 1
            try:
                box_item = box.boxitem_set.get(position=pos)
            except ObjectDoesNotExist:
                box_item = BoxItem(box=box)
            reverse_kwargs = {
                'position': pos,
                'box_identifier': box.box_identifier,
                'action_name': 'verify'}
            cell['href'] = reverse(listboard_url_name, kwargs=reverse_kwargs)
            cell['btn_style'] = btn_style.get(box_item.verified)
            cell['btn_label'] = str(pos).zfill(2)
            cell['btn_title'] = box_item.human_readable_identifier or 'empty'
            cell['has_focus'] = str(pos) == position
            cell['box_item'] = box_item
            row['cells'].append(cell)
        rows.append(row)
    return {'headers': header, 'rows': rows}


@register.filter(is_safe=True)
def verified(box_item):
    if not box_item.verified:
        verified = False
    elif box_item.verified == 1:
        verified = True
    elif box_item.verified == -1:
        verified = False
    return '' if not verified else mark_safe(
        '<span title="position verified" class="text text-success"><i class="fa fa-check fa-fw"></i></span>')
