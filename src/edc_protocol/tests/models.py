from django.db import models


class EnrollmentThree(models.Model):
    subject_identifier = models.CharField(max_length=25, null=True)
