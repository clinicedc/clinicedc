from django.conf import settings

from .base_form_validator import BaseFormValidator


class CurrentSiteValidator(BaseFormValidator):
    def __init__(self, current_site=None, **kwargs):
        self.current_site = current_site or settings.SITE_ID
        super().__init__(**kwargs)
