from django.core.management.base import BaseCommand
from edc_metadata.models import CrfMetadata

from edc_appointment.constants import COMPLETE_APPT, INCOMPLETE_APPT
from edc_appointment.forms import AppointmentForm
from edc_appointment.models import Appointment


def close_appointments():
    for obj in Appointment.objects.filter(appt_status=INCOMPLETE_APPT).order_by(
        "subject_identifier", "visit_code", "visit_code_sequence"
    ):
        data = obj.__dict__
        data.update(appt_status=COMPLETE_APPT, appt_close_datetime=obj.modified)
        form = AppointmentForm(data=data, instance=obj)
        form.is_valid()
        try:
            form.save(commit=False)
        except ValueError:
            obj.refresh_from_db()
            print(
                obj.subject_identifier,
                obj.visit_code,
                obj.visit_code_sequence,
                obj.appt_status,
            )
        else:
            obj.refresh_from_db()
            obj.appt_status = COMPLETE_APPT
            obj.save()

    for obj in Appointment.objects.filter(appt_status=COMPLETE_APPT).order_by(
        "subject_identifier", "visit_code", "visit_code_sequence"
    ):
        data = obj.__dict__
        data.update(appt_status=INCOMPLETE_APPT, appt_close_datetime=obj.modified)
        form = AppointmentForm(data=data, instance=obj)
        form.is_valid()
        try:
            form.save(commit=False)
        except ValueError:
            pass
        else:
            obj.refresh_from_db()
            print(
                obj.subject_identifier,
                obj.visit_code,
                obj.visit_code_sequence,
                obj.appt_status,
                CrfMetadata,
            )


class Command(BaseCommand):
    def handle(self, *args, **options):
        close_appointments()
