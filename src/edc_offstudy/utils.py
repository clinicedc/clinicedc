from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from edc_utils import formatted_datetime
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .exceptions import OffstudyError

if TYPE_CHECKING:
    from django.db.models import Model

    from .model_mixins import OffstudyModelMixin


def get_offstudy_model(visit_schedule_name: str | None = None) -> str:
    """Returns the Offstudy model name in label_lower format"""
    if visit_schedule_name:
        visit_schedule = site_visit_schedules.get_visit_schedule(visit_schedule_name)
        return visit_schedule.offstudy_model
    return getattr(settings, "EDC_OFFSTUDY_OFFSTUDY_MODEL", "edc_offstudy.subjectoffstudy")


def get_offstudy_model_cls(
    visit_schedule_name: str | None = None, offstudy_model: str | None = None
) -> OffstudyModelMixin:
    """Returns the Offstudy model class.

    Uses visit_schedule_name to get the class from the visit schedule
    otherwise defaults settings.EDC_OFFSTUDY_OFFSTUDY_MODEL.
    """
    offstudy_model = offstudy_model or get_offstudy_model(visit_schedule_name)
    return django_apps.get_model(offstudy_model)


def raise_if_offstudy(
    source_obj: Model | None = None,
    subject_identifier: str = None,
    report_datetime: datetime = None,
    offstudy_model: str | None = None,
    visit_schedule_name: str | None = None,
) -> OffstudyModelMixin | None:
    """Returns the Offstudy model instance, if fetched for the given
    query criteria, or none.
    """
    obj = None
    offstudy_model_cls = get_offstudy_model_cls(visit_schedule_name, offstudy_model)
    try:
        with transaction.atomic():
            obj = offstudy_model_cls.objects.get(
                subject_identifier=subject_identifier,
                offstudy_datetime__lt=report_datetime,
            )
    except ObjectDoesNotExist:
        pass
    else:
        raise OffstudyError(
            "Subject off study by given date/time. "
            f"Got `{formatted_datetime(report_datetime)}` "
            f"while the offstudy date is `{formatted_datetime(obj.offstudy_datetime)}` "
            f"Subject {subject_identifier}. Source model {source_obj}. "
            f"See also '{offstudy_model_cls._meta.label_lower}'."
        )
    return obj
