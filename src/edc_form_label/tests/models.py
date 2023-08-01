from django.db import models
from django.db.models.deletion import PROTECT
from edc_constants.choices import YES_NO
from edc_crf.model_mixins import CrfModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.models import SubjectVisit


class MyModel(CrfModelMixin, BaseUuidModel):
    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    circumcised = models.CharField(
        verbose_name="Are you circumcised?", max_length=10, choices=YES_NO
    )


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    class Meta(OnScheduleModelMixin.Meta):
        pass


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta(OffScheduleModelMixin.Meta):
        pass
