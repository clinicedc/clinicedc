from django.db import models

from ..classes import site_lab_profiles


class BaseProcessing(models.Model):

    print_labels = models.BooleanField(
        verbose_name='Print aliquot labels now',
        default=True,
        help_text='If checked, labels will be printed immediately.')

    objects = models.Manager()

    def __unicode__(self):
        return self.aliquot.aliquot_identifier

    def save(self, *args, **kwargs):
        lab_profile = site_lab_profiles.registry.get(self.aliquot.receive.requisition_model_name)
        lab_profile().aliquot_by_profile(self.aliquot, self.profile)
        super(BaseProcessing, self).save(*args, **kwargs)

    class Meta:
        abstract = True
