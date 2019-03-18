from django.contrib import admin
from edc_model_admin import ModelAdminModelRedirectMixin, ModelAdminNextUrlRedirectMixin

from .models import (
    CrfOne,
    CrfTwo,
    CrfThree,
    RedirectModel,
    RedirectNextModel,
    Requisition,
)


class BaseModelAdmin:

    search_fields = ("subject_identifier",)

    add_form_template = "edc_model_admin/admin/change_form.html"
    change_form_template = "edc_model_admin/admin/change_form.html"
    change_list_template = "edc_model_admin/admin/change_list.html"


@admin.register(CrfOne)
class CrfOneAdmin(BaseModelAdmin, admin.ModelAdmin):
    pass


@admin.register(RedirectModel)
class RedirectModelAdmin(
    BaseModelAdmin, ModelAdminModelRedirectMixin, admin.ModelAdmin
):
    redirect_app_label = "edc_model_admin"
    redirect_model_name = "crfone"
    redirect_search_field = "subject_identifier"


@admin.register(RedirectNextModel)
class RedirectNextModelAdmin(
    BaseModelAdmin, ModelAdminNextUrlRedirectMixin, admin.ModelAdmin
):
    pass


@admin.register(CrfTwo)
class CrfTwoAdmin(BaseModelAdmin, ModelAdminNextUrlRedirectMixin, admin.ModelAdmin):
    show_save_next = True
    show_cancel = True


@admin.register(CrfThree)
class CrfThreeAdmin(BaseModelAdmin, ModelAdminNextUrlRedirectMixin, admin.ModelAdmin):
    pass


@admin.register(Requisition)
class RequisitionAdmin(
    BaseModelAdmin, ModelAdminNextUrlRedirectMixin, admin.ModelAdmin
):
    show_save_next = True
    show_cancel = True
