from django.db import models

from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow

from ..constants import CLIENT
from ..device_permission import DevicePermissions, DeviceChangePermission
from ..model_mixins import DeviceModelMixin


class TestModel(BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModel2(BaseUuidModel):

    check_device_permissions = False

    report_datetime = models.DateTimeField(default=get_utcnow)


class TestModelPermissions(BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(DeviceModelMixin.Meta):
        device_permissions = DevicePermissions(
            DeviceChangePermission(device_roles=[CLIENT])
        )
