from django.db import models


class AeInitialTmgModelMixin(models.Model):
    tmg_report_datetime = models.DateTimeField(
        verbose_name="Date and time AE reported to TMG",
        blank=True,
        null=True,
        help_text=(
            "AEs ≥ Grade 4 or SAE must be reported to the Trial "
            "Management Group (TMG) within 24 hours"
        ),
    )

    class Meta:
        abstract = True
