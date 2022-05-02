from django.core.checks import Warning, register

from edc_action_item.site_action_items import site_action_items


@register()
def edc_notification_check(app_configs, **kwargs):  # noqa
    errors = []

    for action_cls in site_action_items.registry.items():
        try:
            action_cls.reference_model_cls().history
        except AttributeError:
            errors.append(
                Warning(
                    (
                        f"Reference model used by action mcs {action_cls} "
                        f"has no history manager."
                    ),
                    hint="History manager is need to detect changes.",
                    obj=action_cls,
                    id="edc_action_item.E001",
                )
            )
    return errors
