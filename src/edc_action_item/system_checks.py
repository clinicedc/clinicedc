from django.core.checks import Error, Warning

from .models import ActionItem
from .site_action_items import site_action_items


def edc_action_item_check(app_configs, **kwargs):
    errors = []
    for name, action_cls in site_action_items.registry.items():
        try:
            action_cls.reference_model_cls().history
        except AttributeError as e:
            if "history" not in str(e):
                raise
            errors.append(
                Warning(
                    (
                        f"Reference model used by action mcs {action_cls} "
                        f"has no history manager."
                    ),
                    hint="History manager is need to detect changes.",
                    obj=action_cls,
                    id="edc_action_item.W001",
                )
            )
    for action_item in ActionItem.objects.all():
        if action_item.reference_model != action_item.action_type.reference_model:
            errors.append(
                Error(
                    (
                        "Action item reference model value does not match "
                        "action_type.reference_model. "
                        f"Got {action_item.reference_model} != "
                        f"{action_item.action_type.reference_model}"
                    ),
                    obj=action_item,
                    id="edc_action_item.E001",
                )
            )
        if (
            action_item.related_reference_model
            != action_item.action_type.related_reference_model
        ):
            errors.append(
                Error(
                    (
                        "Action item related_reference_modell value does not match "
                        "action_type.related_reference_model. "
                        f"Got {action_item.related_reference_model} != "
                        f"{action_item.action_type.related_reference_model}"
                    ),
                    obj=action_item,
                    id="edc_action_item.E002",
                )
            )
    return errors
