from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..constants import CLIENT
from ..device_permission import DevicePermissions, DeviceChangePermission


class TestModel(BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModelPermissions(BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta:
        device_permissions = DevicePermissions(
            DeviceChangePermission(device_roles=[CLIENT]))
