from django.core.management.base import BaseCommand, CommandError
from edc_registration.models import RegisteredSubject
from tqdm import tqdm

from edc_appointment.utils import refresh_appointments


class Command(BaseCommand):
    help = (
        "Validate appointment visit code sequences relative to appt_datetime "
        "and reset if needed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--visit-schedule-name",
            dest="visit_schedule_name",
            default=None,
            help="Visit schedule name",
        )

        parser.add_argument(
            "--schedule-name",
            dest="schedule_name",
            default=None,
            help="Schedule name",
        )

    def handle(self, *args, **options):
        visit_schedule_name = options.get("visit_schedule_name")
        if not visit_schedule_name:
            raise CommandError("--visit-schedule-name is required")
        schedule_name = options.get("schedule_name")
        if not schedule_name:
            raise CommandError("--schedule-name is required")
        qs = RegisteredSubject.objects.all()
        for obj in tqdm(qs, total=qs.count()):
            refresh_appointments(
                obj.subject_identifier,
                visit_schedule_name,
                schedule_name,
                warn_only=True,
                skip_get_current_site=True,
            )
