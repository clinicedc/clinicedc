from django.conf import settings

from .address_mixin import AddressMixin
from .base_model import BaseModel
from .base_uuid_model import BaseUuidModel
from .blood_pressure_model_mixin import BloodPressureModelMixin
from .fields import (
    DiastolicPressureField,
    HeightField,
    HostnameModificationField,
    IdentityTypeField,
    InitialsField,
    IsDateEstimatedField,
    IsDateEstimatedFieldNa,
    OtherCharField,
    SystolicPressureField,
    UUIDAutoField,
    UserField,
    WaistCircumferenceField,
    WeightField,
)
from .historical_records import HistoricalRecords
from .report_status_model_mixin import ReportStatusModelMixin
from .url_model_mixin import UrlModelMixin, UrlModelMixinNoReverseMatch


if settings.APP_NAME == "edc_model":
    from ..tests.models import *  # noqa
