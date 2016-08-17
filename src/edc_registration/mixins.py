from django.apps import apps as django_apps
from django.db import models


class RegisteredSubjectMixin(models.Model):

    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50,
        editable=False)

    def save(self, *args, **kwargs):
        self.subject_identifier = self.registered_subject.subject_identifier
        super(RegisteredSubjectMixin, self).save(*args, **kwargs)

    def registered_subject(self):
        app_config = django_apps.get_app_config('edc_registration')
        return app_config.models.get('registered_subject').get(subject_identifier=self.subject_identifier)
