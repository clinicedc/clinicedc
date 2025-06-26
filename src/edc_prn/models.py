# do not delete

from django.db import models


class SingletonPrnModelMixin(models.Model):
    """Enforces one record per subject."""

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
        self.update_singleton_field()
        super().save(*args, **kwargs)

    def update_singleton_field(self) -> None:
        self.singleton_field = self.subject_identifier

    class Meta:
        abstract = True
