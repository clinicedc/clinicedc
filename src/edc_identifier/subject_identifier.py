from django.apps import apps as django_apps
from edc_base.utils import get_utcnow
from edc_protocol import site_protocol_subjects, SiteProtocolNotRegistered

from .research_identifier import ResearchIdentifier
from edc_identifier.exceptions import SubjectIdentifierError
from django.contrib.sites.models import Site


class SubjectIdentifier(ResearchIdentifier):

    template = '{protocol_number}-{site_id}{device_id}{sequence}'
    label = 'subjectidentifier'

    def __init__(self, create_registration=None,
                 enrollment_cap_by_site=None, last_name=None,
                 site=None, **kwargs):
        super().__init__(**kwargs)
        self.create_registration = create_registration
        self.last_name = last_name
        try:
            subject_type_obj = site_protocol_subjects.get(
                name=self.identifier_type,
                model=self.model)
        except SiteProtocolNotRegistered:
            raise SubjectIdentifierError(
                f'Subject type is not registered with site_protocol_subjects. '
                f'Got {self.identifier_type}.{self.model}')
        self.site = site or Site.objects.get_current()
        _, max_subjects = subject_type_obj.fetch_count_or_raise(site=self.site)
        self.padding = len(str(max_subjects))

    def post_identifier(self):
        """Creates a registered subject instance for this
        subject identifier.
        """
        if self.create_registration:
            model = django_apps.get_app_config('edc_registration').model
            model.objects.create(
                subject_identifier=self.identifier,
                site=self.site,
                subject_type=self.identifier_type,
                last_name=self.last_name,
                registration_datetime=get_utcnow())
