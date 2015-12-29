from datetime import datetime
from django.db import models
from django.core.urlresolvers import reverse
from edc_base.model.models import BaseUuidModel
from ..choices import REVIEW_STATUS


class Review(BaseUuidModel):

    title = models.CharField(
        max_length=50,
        editable=False)

    review_datetime = models.DateTimeField(null=True, blank=False)

    review_status = models.CharField(
        max_length=25,
        choices=REVIEW_STATUS)

    comment = models.TextField(
        max_length=500,
        null=True,
        blank=True)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if self.review_status == 'REVIEWED':
            self.review_datetime = datetime.today()
        super(Review, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('admin:lab_clinic_api_review_change', args=(self.id,))

    def __unicode__(self):
        return '%s' % (self.title)

    class Meta:
        app_label = 'lab_clinic_api'
        ordering = ['review_datetime']
