from django.urls import reverse

from .model_admin_changelist_button_mixin import ModelAdminChangelistButtonMixin


class ModelAdminChangelistModelButtonMixin(ModelAdminChangelistButtonMixin):

    """Use a button as a list_display field with a link to add,
    change or changelist.
    """

    def changelist_model_button(
        self,
        app_label,
        model_name,
        reverse_args=None,
        namespace=None,
        change_label=None,
        add_label=None,
        add_querystring=None,
        disabled=None,
        title=None,
    ):
        if disabled:
            changelist_model_button = self.disabled_button(add_label or change_label)
        else:
            app_label = app_label
            model_name = model_name
            if reverse_args:
                changelist_model_button = self.change_model_button(
                    app_label,
                    model_name,
                    reverse_args,
                    namespace=namespace,
                    label=change_label,
                    title=title,
                )
            else:
                changelist_model_button = self.add_model_button(
                    app_label,
                    model_name,
                    label=add_label,
                    querystring=add_querystring,
                    namespace=namespace,
                    title=title,
                )
        return changelist_model_button

    def change_model_button(
        self,
        app_label,
        model_name,
        reverse_args,
        label=None,
        namespace=None,
        title=None,
    ):
        label = label or "change"
        namespace = namespace or "admin"
        url = reverse(f"{namespace}:{app_label}_{model_name}_change", args=reverse_args)
        return self.button_template(label, url=url, title=title)

    def add_model_button(
        self,
        app_label,
        model_name,
        label=None,
        querystring=None,
        namespace=None,
        title=None,
    ):
        label = label or "add"
        namespace = namespace or "admin"
        url = reverse(
            (f"{namespace}:{app_label}_{model_name}_add") + (querystring or "")
        )
        return self.button_template(label, url=url, title=title)

    def changelist_list_button(
        self,
        app_label,
        model_name,
        querystring_value=None,
        label=None,
        disabled=None,
        namespace=None,
        title=None,
    ):
        """Return a button that goes to the app changelist filter for
        this model instance.
        """
        label = label or "change"
        namespace = namespace or "admin"
        querystring = ""
        if querystring_value:
            querystring = f"?q={querystring_value}"
        url = reverse(
            (f"{namespace}:{app_label}_{model_name}_changelist") + querystring
        )
        return self.button_template(label, disabled=disabled, title=title, url=url)

    def disabled_button(self, label):
        return self.button_template(label, disabled="disabled", url="#")
