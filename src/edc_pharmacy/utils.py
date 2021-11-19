from datetime import date, datetime
from typing import Union

import arrow
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .action_items import PrescriptionAction


def convert_to_utc_date(dte: Union[datetime, date]) -> date:
    try:
        dt = dte.date()
    except AttributeError:
        dt = arrow.get(dte).to("utc").date()
    return dt


def create_prescription(
    subject_identifier: str,
    report_datetime: datetime,
    randomizer_name: str,
    medication_name: str,
):
    medication_model_cls = django_apps.get_model("edc_pharmacy.medication")
    rx_model_cls = django_apps.get_model("edc_pharmacy.rx")

    action = PrescriptionAction(subject_identifier=subject_identifier)
    try:
        medication = medication_model_cls.objects.get(name__iexact=medication_name)
    except ObjectDoesNotExist:
        medication = medication_model_cls.objects.create(name=medication_name)
    try:
        rx_model_cls.objects.get(action_identifier=action.action_identifier)
    except ObjectDoesNotExist:
        rx_model_cls.objects.create(
            action_identifier=action.action_identifier,
            subject_identifier=subject_identifier,
            report_datetime=report_datetime,
            rx_date=report_datetime.date(),
            medication=medication,
            randomizer_name=randomizer_name,
        )
