from __future__ import annotations

from ...exceptions import InsufficientQuantityError


def get_location(item):
    return item.box.shelf.room.location


def get_room(item):
    return item.box.shelf.room


def get_shelf(item):
    return item.box.shelf


def repackage(
    new_container_cls,
    unit_qty: int,
    source_container=None,
    box=None,
):
    if source_container.unit_qty - (source_container.unit_qty_out + unit_qty) < 0:
        raise InsufficientQuantityError()
    else:
        new_container = new_container_cls(
            container_type=source_container.container_type,
            medication_lot=source_container.medication_lot,
            unit_qty=unit_qty,
            unit_qty_out=0,
            source_container=source_container,
            box=box,
        )
        new_container.unit_qty = unit_qty
        new_container.save()
        source_container.unit_qty_out += new_container.unit_qty
        source_container.save()
        source_container.refresh_from_db()
    return new_container, source_container
