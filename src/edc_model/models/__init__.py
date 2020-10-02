from django.conf import settings

from .address_mixin import AddressMixin
from .base_model import BaseModel
from .base_uuid_model import BaseUuidModel
from .blood_pressure_model_mixin import BloodPressureModelMixin
from .fields.duration import DurationYearMonthField
from .fields import (
    DiastolicPressureField,
    DurationYMDField,
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
from .utils import duration_to_date, InvalidFormat
from .validators import (
    bp_validator,
    cell_number,
    date_is_future,
    date_is_past,
    date_not_future,
    datetime_is_future,
    datetime_not_future,
    date_is_not_now,
    hm_validator,
    hm_validator2,
    telephone_number,
    ymd_validator,
)

if settings.APP_NAME == "edc_model":
    from ..tests.models import *  # noqa
