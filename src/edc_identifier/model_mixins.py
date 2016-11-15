from django.apps import apps as django_apps
from django.db import models
from django.utils import timezone

edc_device_app_config = django_apps.get_app_config('edc_device')


class IdentifierModelMixin(models.Model):
    """A model mixin for models that store identifiers as allocated."""

    identifier = models.CharField(max_length=36, unique=True, editable=False)
    padding = models.IntegerField(default=4, editable=False)
    sequence_number = models.IntegerField()
    device_id = models.IntegerField(default=0)
    is_derived = models.BooleanField(default=False)
    sequence_app_label = models.CharField(max_length=50, editable=False, default='identifier')
    sequence_model_name = models.CharField(max_length=50, editable=False, default='sequence')

    def __str__(self):
        return self.identifier

    def natural_key(self):
        return (self.identifier, self.device_id, )

    def save(self, *args, **kwargs):
        self.device_id = edc_device_app_config.device_id
        if not self.id:
            if self.is_derived:
                self.sequence_number = 0
            else:
                Sequence = django_apps.get_model('edc_identifier', 'sequence')
                sequence = Sequence.objects.using(
                    kwargs.get('using')).create(device_id=self.device_id)
                self.sequence_number = sequence.pk
        super(IdentifierModelMixin, self).save(*args, **kwargs)

    @property
    def formatted_sequence(self):
        """Returns a padded sequence segment for the identifier"""
        if self.is_derived:
            return ''
        return str(self.sequence_number).rjust(self.padding, '0')

    class Meta:
        abstract = True


class IdentifierHistoryMixin(models.Model):

    identifier = models.CharField(
        max_length=25,
        unique=True
    )

    identifier_type = models.CharField(
        max_length=25,
    )

    identifier_prefix = models.CharField(
        max_length=25,
        null=True,
    )

    created_datetime = models.DateTimeField(
        default=timezone.now)

    def natural_key(self):
        return (self.identifier, )

    class Meta:
        abstract = True
