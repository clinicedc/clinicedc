from django.contrib.admin import AdminSite as DjangoAdminSite
from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

edc_pharmacy_admin = EdcAdminSite(
    name="edc_pharmacy_admin", app_label=AppConfig.name, keep_delete_action=True
)
edc_pharmacy_admin.disable_action("delete_selected")


class EdcPharmacyHistoryAdmin(DjangoAdminSite):
    site_header = "Pharmacy History"
    site_title = "Pharmacy History"
    index_title = "Pharmacy History"
    index_template = "edc_model_admin/admin/index.html"
    app_index_template = "edc_model_admin/admin/app_index.html"
    login_template = "edc_auth/login.html"
    logout_template = "edc_auth/login.html"
    enable_nav_sidebar = False
    final_catch_all_view = True
    site_url = "/administration/"


edc_pharmacy_history_admin = EdcPharmacyHistoryAdmin(name="edc_pharmacy_history_admin")
edc_pharmacy_history_admin.disable_action("delete_selected")
