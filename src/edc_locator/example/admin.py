from django.contrib import admin

from edc_locator.admin import BaseLocatorModelAdmin

from .forms import LocatorForm
from .models import Locator


class LocatorAdmin(BaseLocatorModelAdmin):
    form = LocatorForm
admin.site.register(Locator, LocatorAdmin)
