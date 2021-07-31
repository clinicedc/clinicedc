# from django.contrib import admin
# from edc_model_admin import SimpleHistoryAdmin
# from edc_model_admin.dashboard import ModelAdminCrfDashboardMixin
# from respond_labs.panels import fbc_panel
#
# from edc_blood_results.admin import BloodResultsModelAdminMixin
# from edc_blood_results.fieldsets import BloodResultFieldset
#
# from .forms import BloodResultsFbcForm
# from .models import BloodResultsFbc
#
#
# @admin.register(BloodResultsFbc)
# class BloodResultsFbcAdmin(
#     BloodResultsModelAdminMixin, ModelAdminCrfDashboardMixin, SimpleHistoryAdmin
# ):
#     form = BloodResultsFbcForm
#     fieldsets = BloodResultFieldset(fbc_panel).fieldsets
