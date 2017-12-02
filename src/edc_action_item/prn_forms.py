from django.conf import settings
from edc_prn import Prn, site_prn_forms

from .admin_site import edc_action_item_admin


class ActionPrn(Prn):

    def show_on_subject_dashboard(self, subject_identifier=None, **kwargs):
        return True


prn = ActionPrn(
    model='edc_action_item.actionitem',
    url_namespace=edc_action_item_admin.name,
    allow_add=True,
    verbose_name='Action Items',
    show_on_dashboard=True,
    dashboard_url_name=settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url'),
    fa_icon='fa-bell')
site_prn_forms.register(prn)
