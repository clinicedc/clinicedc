from django.db import models

from edc.subject.registration.models import RegisteredSubject


class OffStudyManager(models.Manager):

    def get_by_natural_key(self, offstudy_date, subject_identifier_as_pk):
        registered_subject = RegisteredSubject.objects.get(subject_identifier_as_pk=subject_identifier_as_pk)
        return self.get(offstudy_date=offstudy_date, registered_subject=registered_subject)
        return self.get()
