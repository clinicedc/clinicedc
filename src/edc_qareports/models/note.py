from django.db.models import UniqueConstraint

from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, default_permissions

from ..model_mixins import NoteModelMixin


class Note(NonUniqueSubjectIdentifierFieldMixin, NoteModelMixin):
    """A model class to capture user / dm notes linked to a data query
    report, such as, unmanaged views.

    Unique constraint is on subject_identifier and the report model.

    See also, NoteModelAdminMixin
    """

    def __str__(self) -> str:
        return f"{self._meta.verbose_name}: {self.subject_identifier}"

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        constraints = (
            UniqueConstraint(
                fields=["report_model", "subject_identifier"],
                name="%(app_label)s_%(class)s_report_model_subj_uniq",
            ),
        )
        indexes = BaseUuidModel.Meta.indexes
        default_permissions = *default_permissions, "viewallsites"
