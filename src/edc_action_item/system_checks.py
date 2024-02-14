from django.core.checks import Warning

from .site_action_items import site_action_items


def edc_action_item_checks(app_configs, **kwargs):
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
    return errors
