import re

from django.apps import apps as django_apps
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from edc_constants.constants import UUID_PATTERN
from uuid import uuid4

from ..exceptions import IdentifierError
from ..subject_identifier import SubjectIdentifier


class NonUniqueSubjectIdentifierFieldMixin(models.Model):
    """An internal model mixin providing a non-unique subject
    identifier field.
    """

    subject_identifier = models.CharField(max_length=50)

    class Meta:
        abstract = True


class UniqueSubjectIdentifierFieldMixin(models.Model):
    """An internal model mixin providing a unique subject identifier
    field.
    """

    subject_identifier = models.CharField(max_length=50, unique=True)

    class Meta:
        abstract = True


class SubjectIdentifierAdditionalFieldsModelMixin(models.Model):
    """An internal model mixin providing additional fields to used
    with the subject identifier field.
    """

    subject_identifier_as_pk = models.UUIDField(default=uuid4, editable=False)

    subject_identifier_aka = models.CharField(
        verbose_name="Subject Identifier a.k.a",
        max_length=50,
        null=True,
        editable=False,
        help_text="track a previously allocated identifier.",
    )

    class Meta:
        abstract = True


class SubjectIdentifierMethodsModelMixin(models.Model):
    """An internal model mixin to add a unique subject identifier
    field and fill it with a unique value for new instances.
    """

    subject_identifier_cls = SubjectIdentifier

    def save(self, *args, **kwargs):
        if not self.id:
            self.subject_identifier = self.update_subject_identifier_on_save()
        super().save(*args, **kwargs)

    def update_subject_identifier_on_save(self):
        """Returns a subject_identifier if not already set.
        """
        if not self.subject_identifier:
            self.subject_identifier = self.get_or_create_identifier()
        elif re.match(UUID_PATTERN, self.subject_identifier):
            self.subject_identifier = self.get_or_create_identifier()
        return self.subject_identifier

    @property
    def registered_subject_model_cls(self):
        """Returns the registered subject model class.
        """
        return django_apps.get_model("edc_registration.registeredsubject")

    def get_or_create_identifier(self):
        """Returns a subject identifier either by retrieving and
        exisiting "subject identifier from RegisteredSubject or
        creating a new and unique "subject" identifier.
        """
        try:
            subject_identifier = self.registered_subject.subject_identifier
        except AttributeError:
            subject_identifier = self.make_new_identifier()
        return subject_identifier

    def make_new_identifier(self):
        """Returns a new and unique identifier.

        Override this if needed.
        """
        subject_identifier = self.subject_identifier_cls(
            identifier_type="subject",
            requesting_model=self._meta.label_lower,
            site=self.site,
        )
        return subject_identifier.identifier

    @property
    def registered_subject(self):
        """Returns a registered subject instance.

        Override this if your query options are different.
        """
        try:
            obj = self.registered_subject_model_cls.objects.get(
                identity_or_pk=self.identity_or_pk
            )
        except self.registered_subject_model_cls.DoesNotExist:
            # means this is a new model instance that creates RS on the
            # post save signal.
            obj = None
        except MultipleObjectsReturned as e:
            raise IdentifierError(
                "Cannot lookup a unique RegisteredSubject instance. "
                "Identity {} is not unique. Got {}".format(self.identity_or_pk, e)
            )
        return obj

    class Meta:
        abstract = True


class UniqueSubjectIdentifierModelMixin(
    UniqueSubjectIdentifierFieldMixin,
    SubjectIdentifierAdditionalFieldsModelMixin,
    SubjectIdentifierMethodsModelMixin,
    models.Model,
):
    """A model mixin for concrete models requiring a unique subject
    identifier field and corresponding fields and methods.
    """

    class Meta:
        abstract = True


class NonUniqueSubjectIdentifierModelMixin(
    NonUniqueSubjectIdentifierFieldMixin,
    SubjectIdentifierAdditionalFieldsModelMixin,
    SubjectIdentifierMethodsModelMixin,
    models.Model,
):
    """A model mixin for concrete models requiring a non-unique
    subject identifier field and corresponding field and methods.
    """

    class Meta:
        abstract = True
