from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import CommandError

from ..exceptions import PrescriptionAlreadyExists, PrescriptionError

if TYPE_CHECKING:
    from ..models import Rx


def create_prescription(
    subject_identifier: str,
    report_datetime: datetime,
    medication_names: list[str],
    randomizer_name: Optional[str] = None,
    site: Optional[Any] = None,
    site_id: Optional[Any] = None,
    apps: Optional[Any] = None,
) -> Rx:
    """Creates a PrescriptionAction and Rx model instance"""
    site_id = site_id or site.id
    medication_model_cls = (apps or django_apps).get_model("edc_pharmacy.medication")
    rx_model_cls = (apps or django_apps).get_model("edc_pharmacy.rx")
    medications = []
    for medication_name in medication_names:
        try:
            obj = medication_model_cls.objects.get(name__iexact=medication_name)
        except ObjectDoesNotExist:
            raise PrescriptionError(
                "Unable to create prescription. Medication does not exist. "
                f"Got {medication_name}"
            )
        else:
            medications.append(obj)
    try:
        rx = rx_model_cls.objects.get(subject_identifier=subject_identifier)
    except ObjectDoesNotExist:
        opts = dict(
            subject_identifier=subject_identifier,
            report_datetime=report_datetime,
            rx_date=report_datetime.date(),
            randomizer_name=randomizer_name,
        )
        if site_id:
            opts.update(site_id=site_id)
        try:
            rx = rx_model_cls.objects.create(**opts)
        except ObjectDoesNotExist as e:
            raise CommandError(f"Site does not exists. site_id={site_id}. Got {e}")
        for obj in medications:
            rx.medications.add(obj)
    else:
        raise PrescriptionAlreadyExists(f"Prescription already exists. Got {rx}")
    return rx
