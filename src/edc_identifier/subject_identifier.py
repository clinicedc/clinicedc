from django.utils import timezone

from edc_registration import get_registered_subject_model_cls

from .research_identifier import ResearchIdentifier


class SubjectIdentifier(ResearchIdentifier):
    template: str = "{protocol_number}-{site_id}{device_id}{sequence}"
    label: str = "subjectidentifier"
    padding: int = 4

    def __init__(self, last_name: str = None, **kwargs):
        self.last_name = last_name
        super().__init__(**kwargs)

    def pre_identifier(self) -> None:
        pass

    def post_identifier(self) -> None:
        """Creates a registered subject instance for this
        subject identifier.
        """
        model = get_registered_subject_model_cls()
        model.objects.create(
            subject_identifier=self.identifier,
            site=self.site,
            subject_type=self.identifier_type,
            last_name=self.last_name,
            registration_datetime=timezone.now(),
        )
