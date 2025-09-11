from __future__ import annotations

from edc_randomization.site_randomizers import site_randomizers

from ...exceptions import (
    InsufficientQuantityError,
    PackagingLotNumberMismatchError,
    PackagingSubjectIdentifierMismatchError,
)


def get_location(item):
    return item.box.shelf.room.location


def get_room(item):
    return item.box.shelf.room


def get_shelf(item):
    return item.box.shelf


def repackage(
    new_container_model_cls=None,
    unit_qty: int = None,
    source_container=None,
    box=None,
    **kwargs,
):
    if source_container.unit_qty - (source_container.unit_qty_out + unit_qty) < 0:
        raise InsufficientQuantityError()
    else:
        new_container = new_container_model_cls(
            container_type=source_container.container_type,
            medication_lot=source_container.medication_lot,
            unit_qty=unit_qty,
            unit_qty_out=0,
            source_container=source_container,
            box=box,
            **kwargs,
        )
        new_container.unit_qty = unit_qty
        new_container.save()
        source_container.unit_qty_out += new_container.unit_qty
        source_container.save()
        source_container.refresh_from_db()
    return new_container, source_container


def repackage_for_subject(
    rando_sid: str = None,
    subject_identifier: str = None,
    randomizer_name=None,
    source_container=None,
    **kwargs,
):
    site_randomizers.get(randomizer_name)
    # confirm sid
    randomization_list = (
        site_randomizers.get(randomizer_name).model_cls().objects.get(sid=rando_sid)
    )
    # confirm assignment matches rando
    if randomization_list.assignment != source_container.medication_lot.assignment:
        raise PackagingLotNumberMismatchError(
            f"Lot number / assignment mismatch. Got sid `{rando_sid}`."
        )
    # confirm subject_identifier matches with sid, if randomized
    if randomization_list.allocated and not subject_identifier:
        raise PackagingSubjectIdentifierMismatchError(
            f"Expected subject identifier. Subject is randomized. Got sid `{rando_sid}`."
        )
    elif not randomization_list.allocated and subject_identifier:
        raise PackagingSubjectIdentifierMismatchError(
            "Did not expect subject identifier. SID has not been allocated. "
            f"Got sid `{rando_sid}`."
        )
    if subject_identifier and randomization_list.subject_identifier != subject_identifier:
        raise PackagingSubjectIdentifierMismatchError(
            f"Subject identifier mismatch. Got sid `{rando_sid}`."
        )
    return repackage(
        rando_sid=rando_sid,
        subject_identifier=subject_identifier,
        source_container=source_container,
        **kwargs,
    )
