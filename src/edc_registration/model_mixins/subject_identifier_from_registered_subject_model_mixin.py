from django.apps import apps as django_apps
from django.db import models

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin


class SubjectIdentifierFromRegisteredSubjectModelMixin(
        NonUniqueSubjectIdentifierFieldMixin, models.Model):

    """A mixin to ensure subject_identifier is on the model and
    always updated by the registration model.
    """

    def save(self, *args, **kwargs):
        self.subject_identifier = self.registration_instance.subject_identifier
        super().save(*args, **kwargs)

    @property
    def registration_instance(self):
        registration_instance = None
        model = django_apps.get_app_config('edc_registration').model
        try:
            registration_instance = model.objects.get(
                subject_identifier=self.subject_identifier)
        except model.DoesNotExist as e:
            raise model.DoesNotExist(
                f'{e} subject_identifier=\'{self.subject_identifier}\','
                f'model=\'{self._meta.label_lower}\'') from e
        return registration_instance

    class Meta:
        abstract = True
