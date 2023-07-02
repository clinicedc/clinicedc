from __future__ import annotations

import re

from django import forms
from django.urls.base import reverse
from django.utils.html import format_html
from edc_constants.constants import UUID_PATTERN
from edc_dashboard.url_names import url_names


class AlreadyConsentedFormMixin:
    def clean(self) -> dict:
        cleaned_data = super().clean()
        r = re.compile(UUID_PATTERN)
        if (
            self.instance.id
            and self.instance.subject_identifier
            and not r.match(self.instance.subject_identifier)
        ):
            url_name = url_names.get("subject_dashboard_url")
            url = reverse(
                url_name,
                kwargs={"subject_identifier": self.instance.subject_identifier},
            )
            raise forms.ValidationError(self.already_consented_validation_message(url))
        return cleaned_data

    def already_consented_validation_url(self, cleaned_data: dict | None = None) -> str:
        url_name = url_names.get("subject_dashboard_url")
        return reverse(
            url_name,
            kwargs={"subject_identifier": self.instance.subject_identifier},
        )

    def already_consented_validation_message(self, cleaned_data: dict | None = None) -> str:
        return format_html(
            'Not allowed. Subject has already consented. See subject <A href="{}">{}</A>',
            self.already_consented_validation_url(cleaned_data),
            self.instance.subject_identifier,
        )
