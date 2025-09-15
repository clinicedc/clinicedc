from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

if TYPE_CHECKING:
    from .models import ActionType


def create_or_update_action_type(
    name: str = None, using: str = None, apps: django_apps = None, **options
) -> ActionType:
    """Returns a model instance of ActionType.

    Gets or creates the ActionType on first pass.

    If model instance exists, updates.
    """

    action_type_model = "edc_action_item.actiontype"
    apps = apps or django_apps

    opts = {}
    action_type_model_cls = apps.get_model(action_type_model)
    if options:
        fields = [f.name for f in action_type_model_cls._meta.get_fields() if f.name != "name"]
        for attr, value in options.items():
            if attr in fields and value is not None:
                opts.update({attr: value})
    try:
        action_type = action_type_model_cls.objects.get(name=name)
    except ObjectDoesNotExist:
        action_type = action_type_model_cls.objects.create(name=name, **opts)
    else:
        if opts:
            for k, v in opts.items():
                setattr(action_type, k, v)
            action_type.save(using=using)
            action_type = action_type_model_cls.objects.get(name=name)
    return action_type
