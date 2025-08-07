from edc_identifier.managers import SubjectIdentifierManager
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel


class DeathReport(UniqueSubjectIdentifierFieldMixin, BaseUuidModel):
    objects = SubjectIdentifierManager()

    def natural_key(self):
        return (self.subject_identifier,)  # noqa
