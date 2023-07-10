from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_sites.model_mixins import SiteModelMixin
from edc_visit_schedule.model_mixins import (
    VisitScheduleFieldsModelMixin,
    VisitScheduleMethodsModelMixin,
)

from ..choices import ENTRY_STATUS, NOT_REQUIRED, REQUIRED
from ..constants import KEYED

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class CrfMetadataModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    SiteModelMixin,
    VisitScheduleMethodsModelMixin,
    VisitScheduleFieldsModelMixin,
    models.Model,
):

    """Mixin for CrfMetadata and RequisitionMetadata models."""

    visit_code = models.CharField(max_length=25)

    visit_code_sequence = models.IntegerField(default=0)

    timepoint = models.DecimalField(null=True, decimal_places=1, max_digits=6)

    model = models.CharField(max_length=50)

    current_entry_title = models.CharField(max_length=250, null=True)

    show_order = models.IntegerField()  # must always be provided!

    entry_status = models.CharField(
        max_length=25, choices=ENTRY_STATUS, default=REQUIRED, db_index=True
    )

    due_datetime = models.DateTimeField(null=True, blank=True)

    report_datetime = models.DateTimeField(null=True, blank=True)

    entry_comment = models.TextField(max_length=250, null=True, blank=True)

    close_datetime = models.DateTimeField(null=True, blank=True)

    fill_datetime = models.DateTimeField(null=True, blank=True)

    def natural_key(self):
        return (
            self.subject_identifier,
            self.visit_schedule_name,
            self.schedule_name,
            self.visit_code,
            self.visit_code_sequence,
            self.model,
        )

    def is_required(self):
        return self.entry_status != NOT_REQUIRED

    def is_not_required(self):
        return not self.is_required()

    def model_instance_query_opts(self) -> dict:
        models_cls = django_apps.get_model(self.model)
        attr = models_cls.related_visit_model_attr()
        return {
            f"{attr}__schedule_name": self.schedule_name,
            f"{attr}__site": self.site,
            f"{attr}__subject_identifier": self.subject_identifier,
            f"{attr}__visit_code": self.visit_code,
            f"{attr}__visit_code_sequence": self.visit_code_sequence,
            f"{attr}__visit_schedule_name": self.visit_schedule_name,
        }

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    @property
    def model_instance(self: Any) -> Any:
        """Returns the CRF/Requisition model instance or None"""
        instance = None
        try:
            instance = self.model_cls.objects.get(**self.model_instance_query_opts())
        except ObjectDoesNotExist:
            pass
        return instance

    def refresh_entry_status(self) -> str:
        """Resets entry_status to the original visit schedule value"""
        if not self.model_instance:
            if self.visit_code_sequence > 0:
                self.entry_status = REQUIRED
            else:
                visit = self.visits.get(self.visit_code)
                for required in [
                    crf.required for crf in visit.crfs if crf.model == self.model
                ]:
                    self.entry_status = REQUIRED if required else NOT_REQUIRED
        else:
            self.entry_status = KEYED
        self.save_base(update_fields=["entry_status"])
        return self.entry_status

    def get_entry_status(self) -> str:
        return self.refresh_entry_status()

    def get_site_on_create(self) -> Site:
        """Expect site instance to be set from the reference model
        instance.
        """
        return self.site

    class Meta:
        abstract = True
        ordering = ("show_order",)
