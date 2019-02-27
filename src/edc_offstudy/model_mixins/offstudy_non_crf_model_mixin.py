from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import options

from ..utils import raise_if_offstudy

if "offstudy_model" not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("offstudy_model",)
if "offstudy_model_cls" not in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("offstudy_model_cls",)


class OffstudyNonCrfModelMixin(models.Model):

    """A mixin for non-CRF models to add the ability to determine
    if the subject is off study as of this non-CRFs report_datetime.

    Requires fields "subject_identifier" and "report_datetime"

    """

    def save(self, *args, **kwargs):
        if not self._meta.offstudy_model_cls and not self._meta.offstudy_model:
            raise ImproperlyConfigured(
                f"Attribute offstudy_model not defined. See {repr(self)}."
            )
        raise_if_offstudy(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            offstudy_model_cls=(
                self._meta.offstudy_model_cls
                or django_apps.get_model(self._meta.offstudy_model)
            ),
        )
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        offstudy_model = None
        offstudy_model_cls = None
