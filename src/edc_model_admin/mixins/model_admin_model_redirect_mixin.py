from django.urls import reverse

from .base_model_admin_redirect_mixin import BaseModelAdminRedirectMixin


class ModelAdminModelRedirectMixin(BaseModelAdminRedirectMixin):

    """Redirect to another model's changelist on add, change or delete."""

    redirect_app_label = None
    redirect_model_name = None
    redirect_search_field = None
    redirect_namespace = "admin"

    def search_value(self, obj):
        def objattr(inst):
            my_inst = inst
            if self.redirect_search_field:
                for name in self.redirect_search_field.split("__"):
                    my_inst = getattr(my_inst, name)
            return my_inst

        try:
            value = objattr(obj)
        except TypeError:
            value = None
        return value

    def redirect_url(self, request, obj, post_url_continue=None, namespace=None):
        namespace = namespace or self.redirect_namespace
        return "{}?q={}".format(
            reverse(
                "{namespace}:{app_label}_{model_name}_changelist".format(
                    namespace=namespace,
                    app_label=self.redirect_app_label,
                    model_name=self.redirect_model_name,
                )
            ),
            self.search_value(obj) or "",
        )

    def redirect_url_on_delete(self, request, obj_display, obj_id, namespace=None):
        namespace = namespace or self.redirect_namespace
        return reverse(
            "{namespace}:{app_label}_{model_name}_changelist".format(
                namespace=namespace,
                app_label=self.redirect_app_label,
                model_name=self.redirect_model_name,
            )
        )
