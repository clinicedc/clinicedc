from django.apps import apps as django_apps

from edc_base.utils import get_utcnow
from edc_protocol.enrollment_cap import EnrollmentCap

from .research_identifier import ResearchIdentifier


class SubjectIdentifier(ResearchIdentifier):

    template = '{protocol_number}-{site_code}{device_id}{sequence}'
    label = 'subjectidentifier'
    enrollment_cap_cls = EnrollmentCap

    def __init__(self, create_registration=None,
                 enrollment_cap_by_site_code=None, last_name=None, **kwargs):
        super().__init__(**kwargs)
        self.create_registration = create_registration
        self.last_name = last_name
        opts = dict(
            name=self.label,
            subject_type=self.identifier_type,
            model=self.model)
        self.enrollment_cap = self.enrollment_cap_cls(
            subject_type_name=self.identifier_type,
            model=self.model)
        if enrollment_cap_by_site_code:
            opts.update(study_site=self.site_code)
        _, max_subjects = self.enrollment_cap.fetch_or_raise_on_cap_met()
        self.padding = len(str(max_subjects))

    def post_identifier(self):
        """Creates a registered subject instance for this
        subject identifier.
        """
        if self.create_registration:
            model = django_apps.get_app_config('edc_registration').model
            model.objects.create(
                subject_identifier=self.identifier,
                study_site=self.site_code,
                subject_type=self.identifier_type,
                last_name=self.last_name,
                registration_datetime=get_utcnow())
