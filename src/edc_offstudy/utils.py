from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from edc_utils import formatted_datetime
from edc_visit_schedule.site_visit_schedules import site_visit_schedules


class OffstudyError(ValidationError):
    pass


def off_all_schedules_or_raise(subject_identifier=None, offstudy_datetime=None):
    """Raises an exception if subject is enrolled to any schedule.
    """
    for visit_schedule in site_visit_schedules.get_visit_schedules().values():
        for schedule in visit_schedule.schedules.values():
            try:
                with transaction.atomic():
                    schedule.onschedule_model_cls.objects.get(
                        subject_identifier=subject_identifier
                    )
            except ObjectDoesNotExist:
                pass
            else:
                try:
                    with transaction.atomic():
                        schedule.offschedule_model_cls.objects.get(
                            subject_identifier=subject_identifier
                        )
                except ObjectDoesNotExist:
                    model_name = (
                        schedule.offschedule_model_cls()._meta.verbose_name.title()
                    )
                    offschedule_date = formatted_datetime(offstudy_datetime)
                    raise OffstudyError(
                        f"Subject is on schedule on this date. See form "
                        f"'{model_name}'. "
                        f"Got subject_identifier='{subject_identifier}', "
                        f"schedule='{visit_schedule.name}.{schedule.name}, '"
                        f"offschedule date='{offschedule_date}'"
                    )
    return True


def raise_if_offstudy(
    subject_identifier=None, report_datetime=None, offstudy_model_cls=None
):
    try:
        with transaction.atomic():
            offstudy_model_cls.objects.get(
                subject_identifier=subject_identifier,
                offstudy_datetime__lt=report_datetime,
            )
    except ObjectDoesNotExist:
        pass
    else:
        verbose_name = offstudy_model_cls._meta.verbose_name
        raise OffstudyError(
            f"Report date comes after subject's off-study date. "
            f"Got report_datetime={formatted_datetime(report_datetime)} "
            f"See '{verbose_name.title()}'."
        )
