from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.sites.managers import CurrentSiteManager as DjangoCurrentSiteManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, models, transaction

from edc_constants.constants import INCOMPLETE, NOT_APPLICABLE, OTHER

from .constants import MISSED_VISIT
from .exceptions import RelatedVisitReasonError

if TYPE_CHECKING:
    from edc_appointment.models import Appointment


class CrfModelManager(models.Manager):
    """A manager class for Crf models, models that have an FK to
    the visit model.
    """

    use_in_migrations = True

    def get_by_natural_key(
        self,
        subject_identifier,
        visit_schedule_name,
        schedule_name,
        visit_code,
        visit_code_sequence,
    ):
        instance = self.model.visit_model_cls().objects.get_by_natural_key(
            subject_identifier,
            visit_schedule_name,
            schedule_name,
            visit_code,
            visit_code_sequence,
        )
        return self.get(**{self.model.related_visit_model_attr(): instance})


class VisitModelManager(models.Manager):
    """A manager class for related visit models (e.g. subject_visit)."""

    use_in_migrations = True

    def get_by_natural_key(
        self,
        subject_identifier,
        visit_schedule_name,
        schedule_name,
        visit_code,
        visit_code_sequence,
    ):
        return self.get(
            subject_identifier=subject_identifier,
            visit_schedule_name=visit_schedule_name,
            schedule_name=schedule_name,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
        )

    def create_missed_extras(self) -> dict:
        """Extra options to use when auto-creating a visit
        model instance with reason=missed.

        See `create_missed_from_appointment`.
        """
        return {}

    def create_missed_from_appointment(
        self,
        appointment: Appointment,
        reason_missed: str | None = None,
        reason_missed_other: str | None = None,
    ):
        """Creates a subject visit model instance automatically
        for a missed appointment (appt_timing=missed).

        Raises if the visit model instance already exists and
        has reason!=missed.
        """
        try:
            subject_visit = self.get(appointment=appointment)
        except ObjectDoesNotExist:
            opts = dict(
                appointment=appointment,
                comments="[auto-created]",
                info_source=NOT_APPLICABLE,
                reason=MISSED_VISIT,
                reason_missed=reason_missed or OTHER,
                reason_missed_other=reason_missed_other or "[auto-created]",
                report_datetime=appointment.appt_datetime,
                schedule_name=appointment.schedule_name,
                subject_identifier=appointment.subject_identifier,
                survival_status=NOT_APPLICABLE,
                visit_code=appointment.visit_code,
                visit_code_sequence=appointment.visit_code_sequence,
                visit_schedule_name=appointment.visit_schedule_name,
            )
            opts.update(**self.create_missed_extras())
            try:
                with transaction.atomic():
                    obj = self.create(**opts)
            except IntegrityError:
                pass
            obj.document_status = INCOMPLETE
            obj.save(update_fields=["document_status"])
        else:
            if subject_visit.reason != MISSED_VISIT:
                raise RelatedVisitReasonError(
                    f"Subject visit already exists. Reason=`{subject_visit.reason}`"
                )


class VisitCurrentSiteManager(DjangoCurrentSiteManager, VisitModelManager):
    use_in_migrations = True

    pass


class CrfCurrentSiteManager(DjangoCurrentSiteManager, CrfModelManager):
    use_in_migrations = True

    pass
