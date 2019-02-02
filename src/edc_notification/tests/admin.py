from django.contrib.admin.decorators import register
from django.contrib import admin
from edc_model_admin import ModelAdminFormInstructionsMixin

from ..admin_site import edc_notification_admin
from ..modeladmin_mixins import NotificationModelAdminMixin
from .models import AE


class ModelAdminMixin(NotificationModelAdminMixin, ModelAdminFormInstructionsMixin):

    pass


@register(AE, site=edc_notification_admin)
class AEAdmin(ModelAdminMixin, admin.ModelAdmin):

    model = AE
