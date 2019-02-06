from django.views.generic.base import ContextMixin
from edc_registration.models import RegisteredSubject


class RegisteredSubjectViewMixin(ContextMixin):

    """Adds the subject_identifier to the context.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_identifier = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.subject_identifier = self.kwargs.get("subject_identifier")
        obj = RegisteredSubject.objects.get(subject_identifier=self.subject_identifier)
        context.update(
            subject_identifier=self.subject_identifier,
            gender=obj.gender,
            dob=obj.dob,
            initials=obj.initials,
            identity=obj.identity,
            firstname=obj.first_name,
            lastname=obj.last_name,
        )
        return context
