from edc_action_item.admin_site import edc_action_item_admin

from .models import FormOne, FormTwo

edc_action_item_admin.register(FormOne)
edc_action_item_admin.register(FormTwo)
