import re

from django.apps import apps as django_apps
from django.views.generic.base import ContextMixin
from edc_registration.models import RegisteredSubject
from edc_registration.exceptions import RegisteredSubjectError


class RegisteredSubjectViewMixin(ContextMixin):

    """Adds the subject_identifier to the context.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.subject_identifier = self.kwargs.get("subject_identifier")
        if self.subject_identifier:
            app_config = django_apps.get_app_config("edc_identifier")
            if not re.match(
                app_config.subject_identifier_pattern, self.subject_identifier
            ):
                raise RegisteredSubjectError(
                    f"Invalid subject identifier format. "
                    f"Valid pattern is `{app_config.subject_identifier_pattern}`. "
                    f"See AppConfig in `edc_identifier.subject_identifier_pattern`. "
                    f"Got `{self.subject_identifier}`."
                )
            obj = RegisteredSubject.objects.get(
                subject_identifier=self.subject_identifier
            )
            context.update(
                subject_identifier=obj.subject_identifier,
                gender=obj.gender,
                dob=obj.dob,
                initials=obj.initials,
                identity=obj.identity,
                firstname=obj.first_name,
                lastname=obj.last_name,
                registered_subject=obj,
                registered_subject_pk=str(obj.pk),
            )
        return context
