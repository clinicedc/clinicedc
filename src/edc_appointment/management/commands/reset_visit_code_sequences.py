import sys

from django.core.management.base import BaseCommand
from edc_registration.models import RegisteredSubject
from tqdm import tqdm

from edc_appointment.models import Appointment
from edc_appointment.utils import reset_visit_code_sequence_or_pass


class Command(BaseCommand):
    help = (
        "Validate appointment visit code sequences relative to appt_datetime "
        "and reset if needed."
    )

    def handle(self, *args, **options):
        sys.stdout.write(
            "Validating (and resetting, if needed) appointment visit code sequences ...\n"
        )
        qs_rs = RegisteredSubject.objects.all().order_by("subject_identifier")
        for obj in tqdm(qs_rs, total=qs_rs.count()):
            qs = Appointment.objects.filter(
                subject_identifier=obj.subject_identifier,
                visit_code_sequence=0,
            ).order_by("subject_identifier", "visit_code")
            for appointment in qs:
                reset_visit_code_sequence_or_pass(
                    subject_identifier=appointment.subject_identifier,
                    visit_schedule_name=appointment.visit_schedule_name,
                    schedule_name=appointment.schedule_name,
                    visit_code=appointment.visit_code,
                    write_stdout=True,
                )
