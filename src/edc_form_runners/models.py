from django.contrib.sites.models import Site
from django.db import models
from django.db.models import PROTECT, Index, UniqueConstraint
from edc_constants.constants import DONE, IN_PROGRESS, NEW
from edc_model.models import BaseUuidModel


class Issue(BaseUuidModel):
    session_id = models.UUIDField(null=True)
    session_datetime = models.DateTimeField(null=True)
    label_lower = models.CharField(max_length=150)
    verbose_name = models.CharField(max_length=150)
    subject_identifier = models.CharField(max_length=150)
    visit_code = models.CharField(max_length=150)
    visit_code_sequence = models.CharField(max_length=150)
    field_name = models.CharField(max_length=150)
    raw_message = models.TextField(null=True)
    message = models.TextField(null=True)
    short_message = models.CharField(max_length=250, null=True)
    response = models.CharField(max_length=250, null=True)
    src_id = models.UUIDField(null=True)
    src_revision = models.CharField(max_length=150, null=True)
    src_report_datetime = models.DateTimeField(null=True)
    src_modified_datetime = models.DateTimeField(null=True)
    src_user_modified = models.CharField(max_length=150, null=True)
    site = models.ForeignKey(Site, on_delete=PROTECT)
    status = models.CharField(
        max_length=15,
        choices=((NEW, "New"), (IN_PROGRESS, "In progress"), (DONE, "Done")),
        default=NEW,
    )
    extra_formfields = models.TextField(null=True)
    ignore_formfields = models.TextField(null=True)

    def __str__(self):
        return (
            f"{self.subject_identifier} {self.visit_code}.{self.visit_code_sequence} "
            f"{self.verbose_name} ({self.src_revision.split(':')[0]}):{self.field_name} "
            f"{self.message}."
        )

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        constraints = [
            UniqueConstraint(
                fields=[
                    "label_lower",
                    "subject_identifier",
                    "field_name",
                    "visit_code",
                    "visit_code_sequence",
                ],
                name="unique_label_lower_subject_identifier_etc",
            )
        ]
        indexes = [
            Index(fields=["label_lower", "field_name", "short_message"]),
            Index(
                fields=[
                    "subject_identifier",
                    "visit_code",
                    "visit_code_sequence",
                    "short_message",
                ],
            ),
        ]
