from django.db import connection
from django.db.models.signals import post_save, pre_save

from .site_action_items import site_action_items


def fix_null_historical_action_identifier(app_label, models):
    """Fix null action_identifiers from previous versions.
    """
    with connection.cursor() as cursor:
        for model in models:
            cursor.execute(
                f'update {app_label}_historical{model} '
                f'set action_identifier=HEX(id) '
                'where action_identifier is null')


def fix_null_action_item_fk(apps, app_label, models):
    """Re-save instances to update action_item FK.
    """
    post_save.disconnect(dispatch_uid='serialize_on_save')
    pre_save.disconnect(dispatch_uid='requires_consent_on_pre_save')
    for model in models:
        model_cls = apps.get_model(app_label, model)
        model_cls.action_name = [
            action.name for action in site_action_items.registry.values()
            if action.reference_model.split('.')[1].lower() ==
            model.lower()][0]
        for obj in model_cls.objects.all():
            obj.save()
