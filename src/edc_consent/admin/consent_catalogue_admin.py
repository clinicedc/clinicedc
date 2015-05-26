from django.contrib import admin


from simple_history.admin import SimpleHistoryAdmin

from ..forms import ConsentCatalogueForm
from ..models import ConsentCatalogue


class ConsentCatalogueAdmin(SimpleHistoryAdmin):
    form = ConsentCatalogueForm
    list_display = ('name', 'version', 'consent_type', 'start_datetime', 'end_datetime')
    list_filter = ('consent_type', 'created')
admin.site.register(ConsentCatalogue, ConsentCatalogueAdmin)
