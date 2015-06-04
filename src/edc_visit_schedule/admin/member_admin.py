from django.contrib import admin

from edc_base.modeladmin.admin import BaseModelAdmin

from ..forms import MemberForm
from ..models import Member


class MemberAdmin (BaseModelAdmin):

    form = MemberForm

    list_display = ('content_type_map', 'category', 'visible',
                    'user_created', 'user_modified', 'created', 'modified')

    list_filter = ('category',)

    search_fields = ('id',)

admin.site.register(Member, MemberAdmin)
