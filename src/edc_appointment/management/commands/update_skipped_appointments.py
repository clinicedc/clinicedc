from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from tqdm import tqdm

from edc_appointment.skip_appointments import (
    SkipAppointments,
    SkipAppointmentsValueError,
)
from edc_appointment.utils import get_allow_skipped_appt_using
from edc_registration.models import RegisteredSubject

style = color_style()


class Command(BaseCommand):
    help = "Update skipped appointments"

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        errors: dict[str, list[str]] = {}
        for model in get_allow_skipped_appt_using():
            crf_model_cls = django_apps.get_model(model)
            qs = RegisteredSubject.objects.all().order_by("subject_identifier")
            total = qs.count()
            for subject_identifier in tqdm(qs, total=total):
                for subject_visit in (
                    crf_model_cls.related_visit_model_cls()
                    .objects.filter(
                        subject_identifier=subject_identifier, visit_code_sequence=0
                    )
                    .order_by("report_datetime")
                ):
                    try:
                        crf_obj = crf_model_cls.objects.get(subject_visit=subject_visit)
                    except ObjectDoesNotExist:
                        pass
                    else:
                        try:
                            SkipAppointments(crf_obj).update()
                        except SkipAppointmentsValueError as e:
                            msg = (
                                f"{e}. See {subject_visit.subject_identifier}"
                                f"@{subject_visit.visit_code}."
                            )
                            try:
                                errors[subject_visit.subject_identifier].append(msg)
                            except KeyError:
                                errors.update({subject_visit.subject_identifier: [msg]})
                            print(msg)  # noqa: T201
        print("\nERRORS\n")  # noqa: T201
        for k, v in errors.items():
            print(f"{k} ---------------")  # noqa: T201
            for msg in v:
                print(msg)  # noqa: T201
        print("\n\nDone")  # noqa: T201
