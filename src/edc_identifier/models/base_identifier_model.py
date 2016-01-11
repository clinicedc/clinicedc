from django.db import models
from django.db.models import get_model

from edc_device import Device

from .sequence import Sequence


class BaseIdentifierModel(models.Model):
    """Store identifiers as allocated."""

    identifier = models.CharField(max_length=36, unique=True, editable=False)
    padding = models.IntegerField(default=4, editable=False)
    sequence_number = models.IntegerField()
    device_id = models.IntegerField(default=0)
    is_derived = models.BooleanField(default=False)
    sequence_app_label = models.CharField(max_length=50, editable=False, default='identifier')
    sequence_model_name = models.CharField(max_length=50, editable=False, default='sequence')

    def __unicode__(self):
        return self.identifier

    def natural_key(self):
        return (self.identifier, self.device_id, )

    def save(self, *args, **kwargs):
        device = Device()
        self.device_id = device.device_id
        if not self.id:
            if self.is_derived:
                self.sequence_number = 0
            else:
                Sequence = get_model('edc_identifier', 'sequence')
                sequence = Sequence.objects.using(
                    kwargs.get('using')).create(device_id=self.device_id)
                self.sequence_number = sequence.pk
        super(BaseIdentifierModel, self).save(*args, **kwargs)

    @property
    def formatted_sequence(self):
        """Returns a padded sequence segment for the identifier"""
        if self.is_derived:
            return ''
        return str(self.sequence_number).rjust(self.padding, '0')

    class Meta:
        abstract = True
