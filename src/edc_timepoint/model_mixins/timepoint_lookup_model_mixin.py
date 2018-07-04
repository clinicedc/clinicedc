from django.core.exceptions import ImproperlyConfigured
from django.db import models

from ..timepoint_lookup import TimepointLookup


class TimepointLookupModelMixin(models.Model):

    """Makes a model lookup the timepoint model instance on `save`
    and check if it is a closed before allowing a create or update.

    Note: the timepoint model uses the TimepointModelMixin,
    e.g. Appointment
    """

    timepoint_lookup_cls = TimepointLookup

    def save(self, *args, **kwargs):
        timepoint_lookup = self.timepoint_lookup_cls()
        if timepoint_lookup.timepoint_model == self._meta.label_lower:
            raise ImproperlyConfigured(
                f'Timepoint model cannot use TimepointLookupModelMixin. '
                f'Got {self._meta.label_lower}')
        timepoint_lookup.raise_if_closed(model_obj=self)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
