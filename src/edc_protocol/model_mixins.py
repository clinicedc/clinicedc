from django.apps import apps as django_apps
from django.db import models


class EnrollmentCapError(Exception):
    pass


class EnrollmentCapMixin(models.Model):

    """Blocks new instances once a record count is reached."""

    subject_type = models.CharField(
        max_length=25,
        editable=False)

    enrollment_count = models.IntegerField(editable=False)

    enrollment_cap = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.subject_type, self.enrollment_count, self.enrollment_cap = self.raise_on_enrollment_cap()
        super(EnrollmentCapMixin, self).save(*args, **kwargs)

    def raise_on_enrollment_cap(self, exception_cls=None, app_config=None):
        """Raises an exception if enrollment cap reached for this model and subject_type.

        Note: a cap of -1 means enrollment is unlimited."""

        exception_cls = exception_cls or EnrollmentCapError
        app_config = app_config or django_apps.get_app_config('edc_protocol')
        count = 1
        try:
            subject_type, cap = app_config.enrollment_caps[self._meta.label_lower]
        except KeyError:
            raise EnrollmentCapError(
                'Enrollment cap not defined for \'{}\'. See {} name=\'edc_protocol\'.'.format(
                    self._meta.label_lower, app_config.__class__.__name__))
        if cap >= 0:
            count = self.__class__.objects.filter(subject_type=subject_type).count()
            count += 1  # plus one assuming a record will be added
            if count > cap:
                raise exception_cls(
                    '\'{}\' enrollment cap reached. Got {}/{}.'.format(subject_type, count - 1, cap))
        return subject_type, count, cap or 0

    class Meta:
        abstract = True
