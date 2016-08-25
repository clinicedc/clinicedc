from django.apps import apps as django_apps
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class RegisteredSubjectMixin(models.Model):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        editable=False)

    def save(self, *args, **kwargs):
        self.subject_identifier = self.registered_subject().subject_identifier
        super(RegisteredSubjectMixin, self).save(*args, **kwargs)

    def registered_subject(self):
        subject_model = django_apps.get_app_config('edc_registration').registered_subject_model
        return subject_model.objects.get(subject_identifier=self.subject_identifier)

    class Meta:
        abstract = True


class RegistrationMixin(models.Model):

    """A model mixin that creates or updates RegisteredSubject on save."""

    def allocate_subject_identifier(self):
        pass

    def registration_model_class(self):
        return django_apps.get_app_config('edc_registration').model

    def registration_get_or_create(self):
        try:
            registered_subject = self.registered_subject_model_class.objects.get(
                **self.registered_subject_lookup_options)
        except ObjectDoesNotExist:
            registered_subject = self.registered_subject_model_class.objects.create()
        return registered_subject

    def registration_update_registered_subject(self):
        pass

    def registration_lookup_options(self):
        return {'identity': self.identity}

    class Meta:
        abstract = True
