import arrow
from dateutil.relativedelta import relativedelta
from django.db import models
from edc_sites.models import SiteModelMixin

from ..models import (
    BaseModel,
    BaseUuidModel,
    HistoricalRecords,
    ReportStatusModelMixin,
    cell_number,
    date_is_future,
    date_not_future,
    datetime_is_future,
    datetime_not_future,
    telephone_number,
)


def get_utcnow():
    return arrow.utcnow().datetime


def get_future_date():
    return arrow.utcnow().datetime + relativedelta(days=10)


class SimpleModel(BaseModel):
    f1 = models.CharField(max_length=10, null=True)
    dt1 = models.DateTimeField(null=True)
    d1 = models.DateField(null=True)
    ago = models.CharField(max_length=25, null=True)
    report_datetime = models.DateTimeField(null=True)


class BasicModel(BaseModel):
    f1 = models.CharField(max_length=10)
    f2 = models.CharField(max_length=10)


class BasicModelWithStatus(ReportStatusModelMixin, BaseModel):  # type: ignore
    f1 = models.CharField(max_length=10)


class ModelWithHistory(SiteModelMixin, BaseUuidModel):
    f1 = models.CharField(max_length=10, default="1")

    history = HistoricalRecords()


class ModelWithDateValidators(BaseModel):
    datetime_not_future = models.DateTimeField(
        validators=[datetime_not_future], default=get_utcnow
    )

    date_not_future = models.DateField(validators=[date_not_future], default=get_utcnow)

    datetime_is_future = models.DateTimeField(
        validators=[datetime_is_future], default=get_future_date
    )

    date_is_future = models.DateField(validators=[date_is_future], default=get_future_date)


class ModelWithPhoneValidators(BaseModel):
    cell = models.CharField(max_length=25, null=True, validators=[cell_number])
    tel = models.CharField(max_length=25, null=True, validators=[telephone_number])
