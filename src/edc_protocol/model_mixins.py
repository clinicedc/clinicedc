from django.db import models
from django.db.models import options

from edc_protocol.enrollment_cap import EnrollmentCap

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('subject_type_name', )


class EnrollmentCapModelMixin(models.Model):

    """Blocks new instances once a record count is reached."""

    enrollment_cap_cls = EnrollmentCap

    cap_count = models.IntegerField(editable=False)

    cap = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            try:
                subject_type_name = self.subject_type_name
            except AttributeError:
                subject_type_name = self._meta.subject_type_name
            enrollment_cap = EnrollmentCap(
                model=self, subject_type_name=subject_type_name)
            self.cap_count, self.cap = enrollment_cap.fetch_or_raise_on_cap_met()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        subject_type_name = None
