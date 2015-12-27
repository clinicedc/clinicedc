from django.db import models

from edc_base.model.models import BaseUuidModel


class Holiday(BaseUuidModel):

    holiday_name = models.CharField(
        max_length=25,
        default='holiday')
    holiday_date = models.DateField(
        unique=True)

    objects = models.Manager()

    def __unicode__(self):
        return "%s on %s" % (self.holiday_name, self.holiday_date)

    class Meta:
        ordering = ['holiday_date', ]
        app_label = 'edc_appointment'
