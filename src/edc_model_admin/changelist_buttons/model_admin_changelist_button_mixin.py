from django.urls import reverse
from django.utils.html import format_html


class ModelAdminChangelistButtonMixin:

    changelist_model_button_template = (
        '<a href="{{url}}" class="button" title="{{title}}" {{disabled}}>{label}</a>'
    )

    def button(
        self,
        url_name,
        reverse_args,
        disabled=None,
        label=None,
        title=None,
        namespace=None,
    ):
        label = label or "change"
        if namespace:
            url_name = f"{namespace}:{url_name}"
        url = reverse(url_name, args=reverse_args)
        return self.button_template(label, url=url, disabled=disabled, title=title)

    def change_button(
        self,
        url_name,
        reverse_args,
        disabled=None,
        label=None,
        title=None,
        namespace=None,
    ):
        label = label or "change"
        if namespace:
            url_name = f"{namespace}:{url_name}"
        url = reverse(url_name, args=reverse_args)
        return self.button_template(label, url=url, disabled=disabled, title=title)

    def add_button(
        self,
        url_name,
        disabled=None,
        label=None,
        querystring=None,
        namespace=None,
        title=None,
    ):
        label = label or "add"
        if namespace:
            url_name = f"{namespace}:{url_name}"
        url = reverse(url_name) + "" if querystring is None else querystring
        return self.button_template(label, url=url, disabled=disabled, title=title)

    def button_template(self, label, disabled=None, title=None, url=None):
        title = title or ""
        disabled = "disabled" if disabled else ""
        if disabled or not url:
            url = "#"
        button_template = self.changelist_model_button_template.format(label=label)
        button_template = format_html(
            button_template, disabled=disabled, title=title, url=url
        )
        return button_template
