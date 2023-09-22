from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import color_style
from edc_visit_schedule.constants import DAY1
from tqdm import tqdm

from edc_appointment.skip_appointments import SkipAppointments

style = color_style()


class Command(BaseCommand):
    help = "Update skipped appointments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            dest="model",
            action="store",
            nargs="?",
            help="CRF model in label_lower format",
        )
        parser.add_argument(
            "--related_visit",
            dest="related_visit",
            default=settings.SUBJECT_VISIT_MODEL,
            action="store",
            nargs="?",
            help="Related visit model label_lower with or without app_label",
        )

    def handle(self, *args, **options) -> None:
        try:
            related_visit_model_cls = django_apps.get_model(options["related_visit"])
        except LookupError as e:
            raise CommandError(e)
        model = options["model"]
        try:
            app_label = model.split(".")[0]
        except KeyError:
            app_label = options["subject_visit"].split(".")[0]
        except AttributeError as e:
            raise CommandError(f"{e}. Specify a CRF model in label_lower format")
        crf_model_cls = django_apps.get_model(f"{app_label}.{model.split('.')[1]}")
        related_visits = related_visit_model_cls.objects.filter(
            visit_code=DAY1, visit_code_sequence=0
        ).order_by("subject_identifier")
        total = related_visits.count()
        for related_visit in tqdm(related_visits, total=total):
            try:
                obj = crf_model_cls.objects.get(subject_visit=related_visit)
            except ObjectDoesNotExist:
                pass
            else:
                SkipAppointments(obj).skip_to_next()
