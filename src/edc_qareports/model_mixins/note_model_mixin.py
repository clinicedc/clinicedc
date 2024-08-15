from django.apps import apps as django_apps
from django.db import models
from edc_model.models import BaseUuidModel
from edc_sites.model_mixins import SiteModelMixin
from edc_utils import get_utcnow

from ..choices import NOTE_STATUSES


class NoteModelMixin(SiteModelMixin, BaseUuidModel):
    """Model mixin to link form (e.g. note) to a data query report,
    such as, unmanaged views.

    See also, NoteModelAdminMixin
    """

    report_model = models.CharField(max_length=150)

    report_datetime = models.DateTimeField(default=get_utcnow)

    note = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=25, choices=NOTE_STATUSES, null=True, blank=False)

    @property
    def report_model_cls(self):
        return django_apps.get_model(self.report_model)

    class Meta:
        abstract = True
