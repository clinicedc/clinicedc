from .base_registered_subject import BaseRegisteredSubject


class RegisteredSubject(BaseRegisteredSubject):

    class Meta(BaseRegisteredSubject.Meta):
        app_label = "edc_registration"
