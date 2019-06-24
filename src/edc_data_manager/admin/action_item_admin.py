from django.contrib.admin.decorators import register
from edc_action_item.admin import ActionItemAdmin as BaseActionItemAdmin

from ..admin_site import edc_data_manager_admin
from ..models import DataManagerActionItem


@register(DataManagerActionItem, site=edc_data_manager_admin)
class DataManagerActionItemAdmin(BaseActionItemAdmin):
    pass
