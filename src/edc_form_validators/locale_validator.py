from django.conf import settings

from .base_form_validator import BaseFormValidator


class LocaleValidator(BaseFormValidator):
    def __init__(self, locale: str | None = None, **kwargs):
        self.locale = locale or settings.LANGUAGE_CODE
        super().__init__(**kwargs)
