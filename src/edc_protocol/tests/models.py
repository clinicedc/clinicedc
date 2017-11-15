from django.db import models

from ..model_mixins import EnrollmentCapModelMixin


class Enrollment(EnrollmentCapModelMixin, models.Model):

    subject_identifier = models.CharField(max_length=25, null=True)

    subject_type = models.CharField(max_length=25, default='subject')
