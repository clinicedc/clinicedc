from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse, NoReverseMatch
from edc_metadata.next_form_getter import NextFormGetter
from urllib.parse import urlencode

from .base_model_admin_redirect_mixin import BaseModelAdminRedirectMixin


class ModelAdminNextUrlRedirectError(Exception):
    pass


class ModelAdminNextUrlError(Exception):
    pass


class ModelAdminNextUrlRedirectMixin(BaseModelAdminRedirectMixin):

    """Redirect on add, change, delete by reversing a url_name
    in the querystring OR clicking Save Next.

    In your url &next=my_app:my_url_name,arg1,arg2&agr1=value1&arg2=
    value2&arg3=value3&arg4=value4...etc.
    """

    # this func is required if show_save_next=True
    # use edc_metadata.get_next_required_form
    next_form_getter_cls = NextFormGetter

    # need to override admin change_form template for these to wrrk
    show_save_next = False
    show_cancel = False

    next_querystring_attr = "next"

    def extra_context(self, extra_context=None):
        """Adds the booleans for the savenext and cancel buttons
        to the context.

        These are also referred to in the submit_line.html.
        """
        extra_context = extra_context or {}
        if self.show_save_next:
            extra_context.update(show_save_next=self.show_save_next)
        if self.show_cancel:
            extra_context.update(show_cancel=self.show_cancel)
        return extra_context

    def add_view(self, request, form_url="", extra_context=None):
        """Redirect before save on "cancel", otherwise return
        normal behavior.
        """
        if self.show_cancel and request.POST.get("_cancel"):
            redirect_url = self.get_next_redirect_url(request=request)
            return HttpResponseRedirect(redirect_url)
        extra_context = self.extra_context(extra_context)
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Redirect before save on "cancel", otherwise return
        normal behavior.
        """
        if self.show_cancel and request.POST.get("_cancel"):
            redirect_url = self.get_next_redirect_url(
                request=request, object_id=object_id
            )
            return HttpResponseRedirect(redirect_url)
        extra_context = self.extra_context(extra_context)
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )

    def redirect_url(self, request, obj, post_url_continue=None):
        redirect_url = None
        if self.show_save_next and request.POST.get("_savenext"):
            redirect_url = self.get_savenext_redirect_url(request=request, obj=obj)
            if not redirect_url:
                redirect_url = self.get_next_redirect_url(request=request, obj=obj)
        elif self.show_cancel and request.POST.get("_cancel"):
            redirect_url = self.get_next_redirect_url(request=request, obj=obj)
        elif request.GET.dict().get(self.next_querystring_attr):
            redirect_url = self.get_next_redirect_url(request=request, obj=obj)
        if not redirect_url:
            redirect_url = super().redirect_url(
                request, obj, post_url_continue=post_url_continue
            )
        return redirect_url

    def get_next_redirect_url(self, request=None, **kwargs):
        """Returns a redirect url determined from the "next" attr
        in the querystring.
        """
        redirect_url = None
        next_querystring = request.GET.dict().get(self.next_querystring_attr)
        if next_querystring:
            url_name = next_querystring.split(",")[0]
            options = self.get_next_options(request=request, **kwargs)
            try:
                redirect_url = reverse(url_name, kwargs=options)
            except NoReverseMatch as e:
                msg = f"{e}. Got url_name={url_name}, kwargs={options}."
                try:
                    redirect_url = reverse(url_name)  # retry without kwargs
                except NoReverseMatch:
                    # raise with first exception msg
                    raise ModelAdminNextUrlRedirectError(msg)
        return redirect_url

    def get_savenext_redirect_url(self, request=None, obj=None):
        """Returns a redirect_url for the next form in
        the visit schedule.

        This method expects a CRF model with model mixins
        from edc_visit_tracking and edc_visit_schedule.

        Requires edc_metadata. Queries Metadata models.
        """
        panel_name = None
        redirect_url = self.get_next_redirect_url(request=request)
        getter = self.next_form_getter_cls(model_obj=obj)
        if getter.next_form:
            try:
                panel_name = getter.next_form.panel.name
            except AttributeError:
                panel_name = None
            next_model_cls = django_apps.get_model(getter.next_form.model)
            url_name = "_".join(next_model_cls._meta.label_lower.split("."))
            url_name = f"{self.admin_site.name}:{url_name}"
            lookup_opts = {obj.visit_model_attr(): obj.visit}
            if panel_name:
                lookup_opts.update(panel__name=panel_name)
            try:
                next_obj = next_model_cls.objects.get(**lookup_opts)
            except ObjectDoesNotExist:
                redirect_url = reverse(f"{url_name}_add")
            else:
                redirect_url = reverse(f"{url_name}_change", args=(next_obj.id,))
        next_querystring = request.GET.dict().get(self.next_querystring_attr)
        querystring_opts = self.get_next_options(request=request)
        querystring_opts.update({obj.visit_model_attr(): str(obj.visit.id)})
        if panel_name:
            panel_model_cls = django_apps.get_model("edc_lab.panel")
            panel = panel_model_cls.objects.get(name=panel_name)
            querystring_opts.update(panel=str(panel.id))
        querystring = urlencode(querystring_opts)
        return (
            f"{redirect_url}?{self.next_querystring_attr}="
            f"{next_querystring}&{querystring}"
        )

    def get_next_options(self, request=None, **kwargs):
        """Returns the key/value pairs from the "next" querystring
        as a dictionary.
        """
        attrs = request.GET.dict().get(self.next_querystring_attr).split(",")[1:]
        return {
            k: request.GET.dict().get(k) for k in attrs if request.GET.dict().get(k)
        }
