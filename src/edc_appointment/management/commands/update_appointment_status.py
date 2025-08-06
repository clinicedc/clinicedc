from django.core.management import BaseCommand
from tqdm import tqdm

from edc_appointment.models import Appointment
from edc_appointment.utils import update_appt_status


class Command(BaseCommand):
    help = "Update appointment status for all appointments"

    def handle(self, *args, **options) -> None:
        appointments = Appointment.objects.all().order_by("subject_identifier")
        total = appointments.count()
        for appointment in tqdm(appointments, total=total):
            update_appt_status(appointment, save=True)
        print("\n\nDone")
