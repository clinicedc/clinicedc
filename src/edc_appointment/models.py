from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save

from edc_base.model.models import BaseUuidModel


class Holiday(BaseUuidModel):

    holiday_name = models.CharField(
        max_length=25,
        default='holiday')
    holiday_date = models.DateField(
        unique=True)

    objects = models.Manager()

    def __str__(self):
        return "%s on %s" % (self.holiday_name, self.holiday_date)

    class Meta:
        ordering = ['holiday_date', ]
        app_label = 'edc_appointment'


@receiver(post_save, weak=False, dispatch_uid="appointment_post_save")
def appointment_post_save(sender, instance, raw, created, using, **kwargs):
    """Update the TimePointStatus in appointment if the field is empty."""
    if not raw:
        try:
            if not instance.time_point_status:
                instance.time_point_status
                instance.save(update_fields=['time_point_status'])
        except AttributeError as e:
            if 'time_point_status' not in str(e):
                raise AttributeError(str(e))
