from edc_action_item.admin_site import edc_action_item_admin

from .models import CrfOne, CrfTwo, FormOne, FormTwo, Initial, Followup

edc_action_item_admin.register(CrfOne)
edc_action_item_admin.register(CrfTwo)
edc_action_item_admin.register(FormOne)
edc_action_item_admin.register(FormTwo)
edc_action_item_admin.register(Initial)
edc_action_item_admin.register(Followup)
