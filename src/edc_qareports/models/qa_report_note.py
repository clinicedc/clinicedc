from django.apps import apps as django_apps
from django.db import models
from django.db.models import UniqueConstraint
from edc_constants.constants import FEEDBACK, NEW
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow

from ..choices import QA_NOTE_STATUS


class QaReportNote(NonUniqueSubjectIdentifierFieldMixin, SiteModelMixin, BaseUuidModel):
    """A model class to capture user / dm notes linked to a data query
    report, such as, unmanaged views.

    Unique constraint is on subject_identifier and the report model.

    See also, QaReportWithNoteModelAdminMixin
    """

    report_model = models.CharField(max_length=150)

    report_datetime = models.DateTimeField(default=get_utcnow)

    note = models.TextField(null=True)

    status = models.CharField(max_length=25, default=NEW, choices=QA_NOTE_STATUS)

    def save(self, *args, **kwargs):
        if self.status == NEW:
            self.status = FEEDBACK
        super().save(*args, **kwargs)

    @property
    def report_model_cls(self):
        return django_apps.get_model(self.report_model)

    class Meta(BaseUuidModel.Meta):
        verbose_name = "QA Report Note"
        verbose_name_plural = "QA Report Notes"
        constraints = [
            UniqueConstraint(
                fields=["report_model", "subject_identifier"],
                name="%(app_label)s_%(class)s_report_model_subj_uniq",
            )
        ]
        indexes = BaseUuidModel.Meta.indexes
