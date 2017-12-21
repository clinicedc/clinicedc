from django.apps import apps as django_apps
from django.db import models
from edc_base.model_mixins import BaseUuidModel

from ..choices import PRIORITY
from ..constants import HIGH_PRIORITY


class ActionTypeError(Exception):
    pass


class ActionType(BaseUuidModel):

    name = models.CharField(
        max_length=50,
        unique=True)

    display_name = models.CharField(
        max_length=100)

    model = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    priority = models.CharField(
        max_length=25,
        choices=PRIORITY,
        default=HIGH_PRIORITY)

    show_on_dashboard = models.BooleanField(
        default=False)

    show_link_to_changelist = models.BooleanField(
        default=False)

    create_by_action = models.BooleanField(
        default=True,
        help_text='This action may be created by another action')

    create_by_user = models.BooleanField(
        default=True,
        help_text='This action may be created by the user')

    instructions = models.TextField(
        max_length=250,
        null=True,
        blank=True)

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        self.display_name = self.display_name or self.name
        if self.model:
            model_cls = django_apps.get_model(self.model)
            try:
                if not model_cls.action_cls:
                    raise ActionTypeError(
                        f'Model missing an action class. See {repr(model_cls)}')
            except AttributeError as e:
                if 'action_cls' in str(e):
                    raise ActionTypeError(
                        f'Model not configured for Actions. Are you using the model mixin? '
                        f'See {repr(model_cls)}. Got {e}')
                else:
                    raise
        super().save(*args, **kwargs)
