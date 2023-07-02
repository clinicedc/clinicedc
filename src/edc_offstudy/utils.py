from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from edc_utils import formatted_datetime, to_utc
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from .exceptions import OffstudyError

if TYPE_CHECKING:
    from django.db.models import Model

    from .model_mixins import OffstudyModelMixin


def get_offstudy_model() -> str:
    """Returns the Offstudy model name in label_lower format"""
    return site_visit_schedules.get_offstudy_model()


def get_offstudy_model_cls() -> OffstudyModelMixin:
    """Returns the Offstudy model class.

    Uses visit_schedule_name to get the class from the visit schedule
    otherwise defaults settings.EDC_OFFSTUDY_OFFSTUDY_MODEL.
    """
    return django_apps.get_model(site_visit_schedules.get_offstudy_model())


def raise_if_offstudy(
    source_obj: Model | None = None,
    subject_identifier: str = None,
    report_datetime: datetime = None,
) -> OffstudyModelMixin | None:
    """Returns None or raises OffstudyError"""
    obj = None
    try:
        with transaction.atomic():
            obj = get_offstudy_model_cls().objects.get(
                subject_identifier=subject_identifier,
                offstudy_datetime__lt=to_utc(report_datetime),
            )
    except ObjectDoesNotExist:
        pass
    else:
        msg_part = f"Source model `{source_obj._meta.verbose_name}`." if source_obj else ""
        raise OffstudyError(
            "Subject off study by given date/time. "
            f"Got `{formatted_datetime(report_datetime)}` "
            f"while the offstudy date is `{formatted_datetime(obj.offstudy_datetime)}` "
            f"Subject {subject_identifier}. {msg_part} "
            f"See also '{get_offstudy_model_cls()._meta.verbose_name}'."
        )
    return obj
