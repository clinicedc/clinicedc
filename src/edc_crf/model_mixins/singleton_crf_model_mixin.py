from django.db import models


class SingletonCrfModelMixin(models.Model):
    """Enforces one record per subject.

    Requires CrfModelMixn.
    """

    singleton_field = models.CharField(
        verbose_name="subject identifier",
        max_length=50,
        unique=True,
        help_text="auto updated for unique constraint",
        null=True,
        editable=False,
    )

    def save(self, *args, **kwargs):
        # enforce singleton constraint on instance, 1 per subject
        self.singleton_field = self.related_visit.subject_identifier
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
