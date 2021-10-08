from edc_registration.models import RegisteredSubject


class Subject(RegisteredSubject):
    class Meta:
        proxy = True
        default_permissions = ("view", "export")
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
