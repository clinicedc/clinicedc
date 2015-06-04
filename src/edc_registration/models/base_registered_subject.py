from simple_history.models import HistoricalRecords

from django.db import models
from django_crypto_fields.fields import IdentityField

from edc_base.model.fields import IdentityTypeField
from edc_constants.choices import YES_NO, ALIVE_DEAD_UNKNOWN
from edc_identifier.models import SubjectIdentifierMixin
from edc_subject.models import BaseSubject


class BaseRegisteredSubject(SubjectIdentifierMixin, BaseSubject):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        unique=True,
    )

    registration_identifier = models.CharField(
        max_length=36,
        null=True,
        blank=True,
    )

    site_code = models.CharField(
        verbose_name='Site',
        max_length=25,
        help_text="",
        null=True,
        blank=True,
    )

    relative_identifier = models.CharField(
        verbose_name="Identifier of immediate relation",
        max_length=25,
        null=True,
        blank=True,
        help_text="For example, mother's identifier, if available / appropriate"
    )

    identity = IdentityField(
        null=True,
        blank=True,
    )

    identity_type = IdentityTypeField(
        blank=True,
    )

    survival_status = models.CharField(
        verbose_name='Survival status',
        max_length=15,
        choices=ALIVE_DEAD_UNKNOWN,
        null=True,
        blank=True,
    )

    screening_datetime = models.DateTimeField(
        null=True,
        blank=True,
    )

    registration_datetime = models.DateTimeField(
        null=True,
        blank=True,
    )

    """ for simplicity, if going straight from screen to rando,
        update both registration date and randomization date """
    randomization_datetime = models.DateTimeField(
        null=True,
        blank=True,
    )

    registration_status = models.CharField(
        verbose_name="Registration status",
        max_length=25,
        null=True,
        blank=True,
    )

    comment = models.TextField(
        verbose_name='Comment',
        max_length=250,
        null=True,
        blank=True,
    )

    additional_key = models.CharField(
        max_length=36,
        verbose_name='-',
        editable=False,
        default=None,
        null=True,
        help_text=('A uuid (or some other text value) to be added to bypass the '
                   'unique constraint of just firstname, initials, and dob.'
                   'The default constraint proves limiting since the source model usually has some other'
                   'attribute in additional to first_name, initials and dob which '
                   'is not captured in this model'),
    )

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.identity:
            self.additional_key = None
        super(BaseRegisteredSubject, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        # app_label = 'edc_registration'
        # verbose_name = 'Registered Subject'
        ordering = ['subject_identifier']
        unique_together = ('first_name', 'dob', 'initials', 'additional_key')
