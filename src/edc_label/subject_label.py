from typing import Optional

from django.apps import apps as django_apps
from edc_protocol import Protocol

from .label import Label


class SubjectLabel(Label):
    template_name = None
    registered_subject_model = "edc_registration.registeredsubject"

    def __init__(self, subject_identifier: Optional[str] = None, site=None, **kwargs):
        super().__init__(**kwargs)
        self._registered_subject = None
        self.subject_identifier = subject_identifier
        self.site = site
        self.site_context = {}
        if site:
            self.site_context = {
                "site": str(self.site.id),
                "site_name": str(self.site.name),
                "site_title": str(self.site.siteprofile.title),
            }

    @property
    def registered_subject(self):
        if not self._registered_subject:
            model_cls = django_apps.get_model(self.registered_subject_model)
            self._registered_subject = model_cls.objects.get(
                subject_identifier=self.subject_identifier
            )
        return self._registered_subject

    @property
    def label_context(self) -> dict:
        context = {
            "protocol": Protocol().protocol,
            "subject_identifier": self.registered_subject.subject_identifier,
            "gender": self.registered_subject.gender,
            "dob": self.registered_subject.dob,
            "initials": self.registered_subject.initials,
            "identity": self.registered_subject.identity,
        }
        context.update(self.site_context)
        return context
