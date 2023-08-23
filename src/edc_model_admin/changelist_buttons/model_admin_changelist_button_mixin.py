from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


class ModelAdminChangelistButtonMixin:
    changelist_model_button_template_name = "edc_model_admin/changelist_model_button.html"

    def button(
        self,
        url_name,
        reverse_args,
        disabled=None,
        label=None,
        title=None,
        namespace=None,
    ):
        label = label or _("change")
        if namespace:
            url_name = f"{namespace}:{url_name}"
        url = reverse(url_name, args=reverse_args)
        return self.button_template(label=label, url=url, disabled=disabled, title=title)

    def change_button(
        self,
        url_name,
        reverse_args,
        disabled=None,
        label=None,
        title=None,
        namespace=None,
    ):
        label = label or _("change")
        if namespace:
            url_name = f"{namespace}:{url_name}"
        url = reverse(url_name, args=reverse_args)
        return self.button_template(label=label, url=url, disabled=disabled, title=title)

    def add_button(
        self,
        url_name,
        disabled=None,
        label=None,
        querystring=None,
        namespace=None,
        title=None,
    ):
        label = label or _("add")
        if namespace:
            url_name = f"{namespace}:{url_name}"
        url = reverse(url_name) + "" if querystring is None else querystring
        return self.button_template(label=label, url=url, disabled=disabled, title=title)

    def button_template(
        self,
        label: str = None,
        disabled: str | None = None,
        title: str | None = None,
        url: str | None = None,
    ):
        title = title or ""
        disabled = "disabled" if disabled else ""
        if disabled or not url:
            url = "#"
        context = dict(label=label, url=url, disabled=disabled, title=title)
        return format_html(
            render_to_string(self.changelist_model_button_template_name, context)
        )
