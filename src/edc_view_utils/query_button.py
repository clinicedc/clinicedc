from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from django.apps import apps as django_apps
from django.utils.translation import gettext as _

from .dashboard_model_button import DashboardModelButton

if TYPE_CHECKING:
    from edc_registration.models import RegisteredSubject
    from edc_visit_schedule.models import VisitSchedule


__all__ = ["QueryButton"]


class QueryButtonError(Exception):
    pass


@dataclass
class QueryButton(DashboardModelButton):
    """Dashboard button for access to the DataQuery model
    from edc_data_manager.

    Note:
        visit_schedule: a model instance of VisitSchedule
        See edc_visit_schedule.
    """

    registered_subject: RegisteredSubject = None
    visit_schedule: VisitSchedule = None
    fa_icons: tuple[str, str, str] = field(default=(3 * ("",)))
    colors: tuple[str, str, str] = field(default=(3 * ("default",)))
    verbose_name: str = field(default=None, init=False)

    def __post_init__(self):
        if self.model_obj is not None:
            raise ValueError(f"Invalid. Expected none for 'model_obj'. Got {self.model_obj}.")
        self.model_cls = django_apps.get_model("edc_data_manager.dataquery")
        self.verbose_name = self.metadata_model_obj.verbose_name

    def label(self) -> str:
        return _("Query")

    @property
    def url(self) -> str:
        return "?".join([f"{self.model_cls().get_absolute_url()}", self.querystring])

    @property
    def extra_kwargs(self) -> dict[str, str | int | UUID]:
        if not self.registered_subject:
            self.registered_subject = django_apps.get_model(
                "edc_registration.registeredsubject"
            ).objects.get(subject_identifier=self.appointment.subject_identifier)
        if not self.visit_schedule:
            visit_schedule_model_cls = django_apps.get_model(
                "edc_visit_schedule.visitschedule"
            )
            self.visit_schedule = visit_schedule_model_cls.objects.get(
                visit_schedule_name=self.appointment.visit_schedule_name,
                schedule_name=self.appointment.schedule_name,
                visit_code=self.appointment.visit_code,
            )
        return dict(
            registered_subject=self.registered_subject.id,
            sender=self.user.id,
            visit_schedule=self.visit_schedule.id,
            visit_code_sequence=self.appointment.visit_code_sequence,
            title=self.verbose_name,
        )
