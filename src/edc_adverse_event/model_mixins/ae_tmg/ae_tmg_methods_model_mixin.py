from django.db import models


class AeTmgMethodsModelMixin(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)

    def get_action_item_reason(self):
        return self.ae_initial.ae_description

    def get_search_slug_fields(self) -> tuple[str]:
        fields = super().get_search_slug_fields()
        return *fields, "subject_identifier", "report_status"
