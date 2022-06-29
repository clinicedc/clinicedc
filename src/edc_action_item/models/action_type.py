from django.apps import apps as django_apps
from django.db import models
from edc_constants.constants import HIGH_PRIORITY
from edc_model.models import BaseUuidModel

from ..choices import PRIORITY


class ActionTypeError(Exception):
    pass


class ActionTypeManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, name):
        return self.get(name=name)


class ActionType(BaseUuidModel):

    name = models.CharField(max_length=50, unique=True)

    display_name = models.CharField(max_length=100)

    reference_model = models.CharField(
        max_length=100, null=True, blank=True, help_text="reference model"
    )

    related_reference_model = models.CharField(
        max_length=100, null=True, blank=True, help_text="origin reference model"
    )

    priority = models.CharField(max_length=25, choices=PRIORITY, default=HIGH_PRIORITY)

    show_on_dashboard = models.BooleanField(default=False)

    show_link_to_changelist = models.BooleanField(default=False)

    create_by_action = models.BooleanField(
        default=True, help_text="This action may be created by another action"
    )

    create_by_user = models.BooleanField(
        default=True, help_text="This action may be created by the user"
    )

    instructions = models.TextField(max_length=250, null=True, blank=True)

    objects = ActionTypeManager()

    def __str__(self):
        return self.display_name

    def natural_key(self):
        return (self.name,)  # noqa

    @property
    def reference_model_cls(self):
        model_cls = None
        if self.reference_model:
            try:
                model_cls = django_apps.get_model(self.reference_model)
            except (LookupError, ValueError) as e:
                raise ActionTypeError(f"{e}. Got reference_model=`{self.reference_model}`")
        return model_cls

    def save(self, *args, **kwargs):
        self.display_name = self.display_name or self.name
        if self.reference_model and self.reference_model != "edc_action_item.reference":
            try:
                if not self.reference_model_cls.action_name:
                    raise ActionTypeError(
                        f"Model missing an action class. See {repr(self.reference_model_cls)}"
                    )
            except AttributeError as e:
                if "action_name" in str(e):
                    raise ActionTypeError(
                        f"Model not configured for Actions. Are you using the model mixin? "
                        f"See {repr(self.reference_model_cls)}. Got {e}"
                    )
                else:
                    raise
        super().save(*args, **kwargs)

    class Meta(BaseUuidModel.Meta):
        ordering = ["name"]
        indexes = [models.Index(fields=["id", "name"])]
        default_permissions = ("add", "change", "delete", "view", "export", "import")
