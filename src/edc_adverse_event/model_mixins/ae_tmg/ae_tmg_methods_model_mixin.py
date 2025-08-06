from django.db import models


class AeTmgMethodsModelMixin(models.Model):
    def __str__(self):
        return f"{self.action_identifier[-9:]}"

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.action_identifier,)  # noqa

    def get_action_item_reason(self):
        return self.ae_initial.ae_description

    def get_search_slug_fields(self):
        fields = super().get_search_slug_fields()
        fields.append("subject_identifier")
        fields.append("report_status")
        return fields

    class Meta:
        abstract = True
