import uuid

from django.db import models

from edc_base.model_mixins import BaseUuidModel

from ..model_mixins import UpdatesOrCreatesRegistrationModelMixin


class SubjectModelOne(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):

    screening_identifier = models.CharField(
        max_length=25,
        null=True)

    registration_identifier = models.UUIDField(
        unique=True,
        default=uuid.uuid4)

    dob = models.DateField(null=True)


class SubjectModelTwo(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):

    """Note: registration_unique_field is overridden.
    """

    subject_identifier = models.CharField(
        max_length=25,
        null=True)

    dob = models.DateField(null=True)

    @property
    def registration_unique_field(self):
        return 'subject_identifier'


class SubjectModelThree(UpdatesOrCreatesRegistrationModelMixin, BaseUuidModel):

    """Note: registration_unique_field is overridden.
    """

    subject_identifier = models.CharField(
        max_length=25,
        null=True)

    my_identifier = models.UUIDField(default=uuid.uuid4)

    dob = models.DateField(null=True)

    @property
    def registration_unique_field(self):
        return 'my_identifier'

    @property
    def registered_subject_unique_field(self):
        return 'registration_identifier'
