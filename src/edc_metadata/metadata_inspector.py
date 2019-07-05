from django.conf import settings
from django.contrib.sites.models import Site

from .constants import REQUIRED, KEYED
from .models import CrfMetadata


class MetaDataInspector:

    """Inspects for the given timepoint and form.
    """

    metadata_model_cls = CrfMetadata

    def __init__(self, model_cls=None, visit_schedule=None, subject_visit=None):
        self.model_cls = model_cls
        obj = visit_schedule or subject_visit
        self.visit_schedule_name = obj.visit_schedule_name
        self.schedule_name = obj.schedule_name
        self.visit_code = obj.visit_code

    @property
    def required(self):
        """Returns a list of subject identifiers.
        """
        opts = dict(
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit_code,
            site=Site.objects.get(id=settings.SITE_ID),
            model=self.model_cls._meta.label_lower,
            entry_status=REQUIRED,
        )
        qs = self.metadata_model_cls.objects.values("subject_identifier").filter(**opts)
        return [value_obj.get("subject_identifier") for value_obj in qs]

    @property
    def keyed(self):
        """Returns a list of subject identifiers.
        """
        opts = dict(
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit_code,
            site=Site.objects.get(id=settings.SITE_ID),
            model=self.model_cls._meta.label_lower,
            entry_status=KEYED,
        )
        qs = self.metadata_model_cls.objects.values("subject_identifier").filter(**opts)
        return [value_obj.get("subject_identifier") for value_obj in qs]
