import re

from django.apps import apps as django_apps
from django.db import models

from edc_base.utils import get_uuid
from edc_identifier.subject_identifier import SubjectIdentifier
from edc_identifier.exceptions import IdentifierError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class NonUniqueSubjectIdentifierFieldMixin(models.Model):
    """An internal model mixin providing a non-unique subject identifier field."""
    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50)

    class Meta:
        abstract = True


class UniqueSubjectIdentifierFieldMixin(models.Model):
    """An internal model mixin providing a unique subject identifier field."""
    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        unique=True)

    class Meta:
        abstract = True


class SubjectIdentifierAdditionalFieldsModelMixin(models.Model):
    """An internal model mixin providing additional fields to used with the subject identifier field."""

    subject_identifier_as_pk = models.CharField(
        verbose_name="Subject Identifier as pk",
        max_length=50,
        default=get_uuid,
        editable=False,
    )

    subject_identifier_aka = models.CharField(
        verbose_name="Subject Identifier a.k.a",
        max_length=50,
        null=True,
        editable=False,
        help_text='track a previously allocated identifier.'
    )

    class Meta:
        abstract = True


class SubjectIdentifierMethodsModelMixin(models.Model):
    """An internal model mixin to add a unique subject identifier field and
    fill it with a unique value for new instances."""

    def save(self, *args, **kwargs):
        if not self.id and not self.subject_identifier:
            if not re.match('[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}', self.subject_identifier_as_pk or ''):
                self.subject_identifier_as_pk = get_uuid()
            self.subject_identifier = self.get_or_create_identifier()
        super().save(*args, **kwargs)

    @property
    def registered_subject_model_class(self):
        """Returns the registered subject model class."""
        return django_apps.get_app_config('edc_registration').model

    def get_or_create_identifier(self):
        """Returns a subject identifier either by retrieving and exisiting "subject"
        identifier from RegisteredSubject or creating a new and unique "subject" identifier."""
        try:
            subject_identifier = self.registered_subject.subject_identifier
        except ObjectDoesNotExist:
            subject_identifier = self.make_new_identifier()
        return subject_identifier

    def make_new_identifier(self):
        """Returns a new and unique identifier.

        Override this if needed."""
        subject_identifier = SubjectIdentifier(
            subject_type_name='subject',
            model=self._meta.label_lower,
            study_site=self.study_site,
            create_registration=False)
        return subject_identifier.identifier

    @property
    def registered_subject(self):
        """Returns a registered subject instance.

        Override this if your query options are different."""
        try:
            obj = self.registered_subject_model_class.objects.get(
                identity=self.identity)
        except MultipleObjectsReturned as e:
            raise IdentifierError(
                'Cannot lookup a unique RegisteredSuject instance. '
                'Identity {} is not unique. Got {}'.format(self.identity, e))
        return obj

    class Meta:
        abstract = True


class UniqueSubjectIdentifierModelMixin(
        UniqueSubjectIdentifierFieldMixin,
        SubjectIdentifierAdditionalFieldsModelMixin, SubjectIdentifierMethodsModelMixin, models.Model):
    """A model mixin for concrete models requiring a unique subject identifier field and
    corresponding fields and methods."""
    class Meta:
        abstract = True


class NonUniqueSubjectIdentifierModelMixin(
        NonUniqueSubjectIdentifierFieldMixin,
        SubjectIdentifierAdditionalFieldsModelMixin, SubjectIdentifierMethodsModelMixin, models.Model):
    """A model mixin for concrete models requiring a non-unique subject identifier field and
    corresponding field and methods."""

    class Meta:
        abstract = True
