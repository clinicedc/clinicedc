from typing import List, Optional

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_visit_tracking.constants import SCHEDULED

from ..constants import KEYED, NOT_REQUIRED, REQUIRED


class PersistantSingletonMixin:
    """A mixin to be declared with the PredicateCollection.

    Handles a singleton model that needs to be entered
    at some later visit if not at the intended visit.

    The `required` entry status of CRF metadata is moved to the
    last attended visit in the schedule until the CRF is submitted.
    """

    def persistant_singleton_required(
        self, visit, model=None, exclude_visit_codes: Optional[List[str]] = None
    ) -> bool:
        """Returns True if the CRF model was not completed from any time
        after the exclude_visit_codes

        Updates metadata for other timepoints, except the last, to `not required`
        until the model is submitted.

        CRF model is a singleton.
        """
        model_cls = django_apps.get_model(model)
        try:
            obj = model_cls.objects.get(
                subject_visit__subject_identifier=visit.subject_identifier
            )
        except ObjectDoesNotExist:
            obj = None
            required = (
                True
                if visit == self.get_last_attended_scheduled_visit(visit)
                and visit.visit_code not in exclude_visit_codes
                else False
            )
        else:
            required = False
        if visit and visit.visit_code not in exclude_visit_codes:
            last_attended_visit = self.get_last_attended_scheduled_visit(visit)
            if last_attended_visit:
                self.set_other_crf_metadata_not_required(
                    obj=obj,
                    model_cls=model_cls,
                    last_attended_visit=last_attended_visit,
                )
        return required

    @staticmethod
    def set_other_crf_metadata_not_required(
        obj=None, model_cls=None, last_attended_visit=None
    ):
        """Updates CRF metadata for the given model setting
        all but last visit to NOT_REQUIRED OR, if the model
        has been submitted, all others but the KEYED one as
        NOT_REQUIRED.

        Model must be a singleton
        """
        crf_metadata_model_cls = django_apps.get_model("edc_metadata.crfmetadata")
        model = f"{model_cls._meta.app_label}.{model_cls._meta.model_name}"

        opts = dict(
            subject_identifier=last_attended_visit.subject_identifier,
            model=model,
            visit_schedule_name=last_attended_visit.visit_schedule_name,
            schedule_name=last_attended_visit.schedule_name,
            visit_code_sequence=0,
        )
        if not obj:
            crf_metadata_model_cls.objects.filter(**opts).exclude(
                timepoint=last_attended_visit.appointment.timepoint
            ).update(entry_status=NOT_REQUIRED)
            crf_metadata_model_cls.objects.filter(
                timepoint=last_attended_visit.appointment.timepoint, **opts
            ).update(entry_status=REQUIRED)
        else:
            crf_metadata_model_cls.objects.filter(**opts).exclude(entry_status=KEYED).update(
                entry_status=NOT_REQUIRED
            )

    @staticmethod
    def get_last_attended_scheduled_visit(visit):
        """Returns the last attended `subject_visit` model instance given
        any existing `subject_visit` in the schedule.
        """
        return (
            visit.__class__.objects.filter(
                subject_identifier=visit.subject_identifier,
                reason=SCHEDULED,
                visit_schedule_name=visit.visit_schedule_name,
                schedule_name=visit.schedule_name,
                visit_code_sequence=0,
            )
            .order_by("appointment__timepoint")
            .last()
        )
