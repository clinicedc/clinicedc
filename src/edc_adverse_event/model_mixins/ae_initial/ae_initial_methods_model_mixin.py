from django.apps import apps as django_apps
from django.db import models


class AeInitialMethodsModelMixin(models.Model):
    def __str__(self):
        return f"{self.action_identifier[-9:]} Grade {self.ae_grade}"

    def natural_key(self):
        return (self.action_identifier,)

    def get_action_item_reason(self):
        return self.ae_description

    @property
    def ae_follow_up_model_cls(self):
        return django_apps.get_model(f"{self._meta.app_label}.aefollowup")

    @property
    def ae_follow_ups(self):
        return self.ae_follow_up_model_cls.objects.filter(ae_initial=self).order_by(
            "report_datetime"
        )

    @property
    def description(self):
        """Returns a description."""
        return f"{self.action_identifier[-9:]} Grade-{self.ae_grade}. {self.ae_description}"

    class Meta:
        abstract = True
