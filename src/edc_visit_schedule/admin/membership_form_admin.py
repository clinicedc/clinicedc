from django.contrib import admin

from .base_model_admin import BaseModelAdmin

from ..forms import MembershipFormForm
from ..models import MembershipForm


class MembershipFormAdmin (BaseModelAdmin):

    form = MembershipFormForm

    list_display = (
        'content_type_map', 'category', 'visible', 'user_created',
        'user_modified', 'created', 'modified')

    list_filter = ('category',)

    search_fields = ('id',)

admin.site.register(MembershipForm, MembershipFormAdmin)
