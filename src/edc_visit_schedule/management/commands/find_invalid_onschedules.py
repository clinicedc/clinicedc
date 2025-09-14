from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class Command(BaseCommand):
    help = "List email recipients for each registered notification"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete invalid OnSchedule model instances",
        )

    def handle(self, *args, **options):
        allow_delete = False
        if options["delete"]:
            allow_delete = True
        else:
            print("Checking only")
        subject_schedule_history_cls = django_apps.get_model(
            "edc_visit_schedule.subjectschedulehistory"
        )
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                try:
                    onschedule_model_cls = schedule.onschedule_model_cls
                except LookupError:
                    pass
                else:
                    for onschedule_obj in onschedule_model_cls.objects.all():
                        try:
                            subject_schedule_history_cls.objects.get(
                                subject_identifier=onschedule_obj.subject_identifier,
                                onschedule_model=onschedule_model_cls._meta.label_lower,
                            )
                        except ObjectDoesNotExist:
                            msg = (
                                f"{onschedule_model_cls._meta.label_lower} for "
                                f"{onschedule_obj.subject_identifier} is invalid."
                            )
                            if allow_delete:
                                msg = f"{msg} deleted."
                                onschedule_obj.delete()
                            print(msg)
