from django.db import models


class VisitCodeFieldsModelMixin(models.Model):
    visit_code = models.CharField(max_length=25, null=True, editable=False)

    visit_code_sequence = models.IntegerField(
        verbose_name="Sequence",
        default=0,
        null=True,
        blank=True,
        help_text=(
            "An integer to represent the sequence of additional "
            "appointments relative to the base appointment, 0, needed "
            "to complete data collection for the timepoint. (NNNN.0)"
        ),
    )

    class Meta:
        abstract = True
