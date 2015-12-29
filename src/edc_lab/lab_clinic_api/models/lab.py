from django.db import models

from edc_base.model.models import BaseUuidModel

# TODO: is this used??


class Lab(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=50,
    )
    protocol_identifier = models.CharField(
        max_length=50,
    )
    clinician_initials = models.CharField(
        max_length=3,
    )
    release_status = models.CharField(
        max_length=25,
        blank=True,
        null=True
    )
    panel = models.CharField(
        max_length=250,
        blank=True,
        null=True
    )
    drawn_datetime = models.DateTimeField(
        blank=True,
        null=True
    )
    receive_datetime = models.DateTimeField(
        blank=True,
        null=True
    )
    receive_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True
    )
    aliquot_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True
    )
    condition = models.CharField(
        max_length=250,
        blank=True,
        null=True
    )
    order_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True
    )
    order_datetime = models.DateTimeField(
        blank=True,
        null=True
    )
    result_identifier = models.CharField(
        max_length=25,
        blank=True,
        null=True
    )
    release_datetime = models.DateTimeField(
        blank=True,
        null=True
    )

    # objects = LabManager()

    def __unicode__(self):
        return '%s order %s for %s drawn %s [%s]' % (self.subject_identifier, self.order_identifier, self.panel, self.drawn_datetime.strftime('%Y-%m-%d'), self.release_status)

    class Meta:
        app_label = "lab_clinic_api"
