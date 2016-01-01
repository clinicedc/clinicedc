from django.db import models

from .time_point_status import TimePointStatus


class TimePointStatusMixin(models.Model):

    def save(self, *args, **kwargs):
        using = kwargs.get('using')
        if self.id:
            try:
                TimePointStatus.check_time_point_status(
                    self.get_visit().appointment, using=using)
            except AttributeError:
                TimePointStatus.check_time_point_status(self.appointment, using=using)
        super(TimePointStatusMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
