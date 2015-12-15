from django.db import models


class OffStudyManager(models.Manager):

    def __init__(self, registered_subject_model):
        self.registered_subject_model = registered_subject_model
        super(OffStudyManager, self).__init__()

    def get_by_natural_key(self, offstudy_date, subject_identifier_as_pk):
        registered_subject = self.registered_subject_model.objects.get(subject_identifier_as_pk=subject_identifier_as_pk)
        return self.get(offstudy_date=offstudy_date, registered_subject=registered_subject)
        return self.get()
