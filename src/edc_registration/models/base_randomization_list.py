from django.db import models

from edc_base.model.models import BaseUuidModel
try:
    from edc_sync.mixins import SyncMixin
except ImportError:
    SyncMixin = type('SyncMixin', (object, ), {})


class BaseRandomizationList (BaseUuidModel, SyncMixin):
    """
    You might inherit from RandomizationList to get something like this, assuming your app is 'protocol'

    class RandomizationList (RandomizationListBase):

        feeding_choice = models.CharField("Feeding Choice",
            max_length=2)
        haart_status = models.CharField("Maternal HAART Status",
            max_length=10)
        rx = models.CharField("Study Drug",
            max_length=7)
        feeding_duration = models.IntegerField("Feeding Duration in Months",)

        def __unicode__(self):
            return "%s %s %s (%s)" % (self.sid, self.feeding_choice,self.feeding_duration, self.haart_status)

        class Meta:
            app_labl='protocol'
    """

    sid = models.IntegerField(
        unique=True,
        verbose_name="SID")

    site_name = models.CharField(
        "Registration Site",
        max_length=10)

    site = models.IntegerField("site code")

    registration_datetime = models.DateTimeField("Registration Date and Time")

    subject_identifier = models.CharField(max_length=25)

    class Meta:
        abstract = True
