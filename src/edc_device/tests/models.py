from edc_base.model_mixins import BaseUuidModel
from edc_device.model_mixins import DeviceModelMixin
from django.db import models
from edc_base.utils import get_utcnow


class TestModel(DeviceModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)
