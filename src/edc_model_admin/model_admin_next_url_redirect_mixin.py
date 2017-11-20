from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse, NoReverseMatch
from urllib.parse import urlencode

from .base_model_admin_redirect_mixin import BaseModelAdminRedirectMixin


class ModelAdminNextUrlRedirectError(Exception):
    pass


class ModelAdminNextUrlError(Exception):
    pass


class ModelAdminNextUrlRedirectMixin(BaseModelAdminRedirectMixin):

    """Redirect on add, change, delete by reversing a url_name
    in the querystring OR clicking Save Next.

    In your url &next=my_url_name,arg1,arg2&agr1=value1&arg2=
    value2&arg3=value3&arg4=value4...etc.
    """

    show_save_next = False
    show_cancel = False
    next_querystring_attr = 'next'

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

    def add_view(self, request, form_url='', extra_context=None):
        """Redirect before save on "cancel", otherwise return
        normal behavior.
        """
        if self.show_cancel and request.POST.get('_cancel'):
            redirect_url = self.get_next_redirect_url(request=request)
            return HttpResponseRedirect(redirect_url)
        extra_context = self.extra_context(extra_context)
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Redirect before save on "cancel", otherwise return
        normal behavior.
        """
        if self.show_cancel and request.POST.get('_cancel'):
            redirect_url = self.get_next_redirect_url(request=request)
            return HttpResponseRedirect(redirect_url)
        extra_context = self.extra_context(extra_context)
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def render_delete_form(self, request, context):
        return super().render_delete_form(request, context)

    def delete_view(self, request, object_id, extra_context=None):
        return super().delete_view(request, object_id, extra_context=extra_context)

    def redirect_url(self, request, obj, post_url_continue=None):
        if self.show_save_next and request.POST.get('_savenext'):
            redirect_url = self.get_savenext_redirect_url(
                request=request, obj=obj)
            if not redirect_url:
                redirect_url = self.get_next_redirect_url(request=request)
        elif self.show_cancel and request.POST.get('_cancel'):
            redirect_url = self.get_next_redirect_url(request=request)
        elif request.GET.dict().get(self.next_querystring_attr):
            redirect_url = self.get_next_redirect_url(request=request)
        if not redirect_url:
            redirect_url = super().redirect_url(
                request, obj, post_url_continue=post_url_continue)
        return redirect_url

    def get_next_redirect_url(self, request=None):
        """Returns a redirect url determined from the "next" attr
        in the querystring.
        """
        url_name = request.GET.dict().get(
            self.next_querystring_attr).split(',')[0]
        options = self.get_next_options(request=request)
        try:
            redirect_url = reverse(url_name, kwargs=options)
        except NoReverseMatch as e:
            raise ModelAdminNextUrlRedirectError(
                f'{e}. Got url_name={url_name}, kwargs={options}.')
        return redirect_url

    def get_savenext_redirect_url(self, request=None, obj=None):
        """Returns a redirect_url for the next form in the visit schedule.

        This method expects a CRF model with model mixins from edc_visit_tracking
        and edc_visit_schedule.
        """
        try:
            next_form = obj.visit.visit.next_form(model=obj._meta.label_lower)
        except AttributeError as e:
            raise ModelAdminNextUrlError(
                f'{e} Model {repr(obj)}. Check model class declaration uses '
                f'required model mixins from edc_visit_tracking and edc_visit_schedule.')
        if next_form:
            try:
                panel_name = next_form.panel.name
            except AttributeError:
                panel_name = None
            next_model_cls = django_apps.get_model(next_form.model)
            url_name = '_'.join(
                next_model_cls._meta.label_lower.split('.'))
            url_name = f'{self.admin_site.name}:{url_name}'
            opts = {obj.visit_model_attr(): obj.visit}
            if panel_name:
                opts.update(panel_name=panel_name)
            try:
                next_obj = next_model_cls.objects.get(**opts)
            except ObjectDoesNotExist:
                redirect_url = reverse(f'{url_name}_add')
            else:
                redirect_url = reverse(
                    f'{url_name}_change', args=(next_obj.id, ))
        next_querystring = request.GET.dict().get(self.next_querystring_attr)
        options = self.get_next_options(request=request)
        if panel_name:
            options.update(panel_name=panel_name)
        options.update({obj.visit_model_attr(): str(obj.visit.id)})
        querystring = urlencode(options)
        return f'{redirect_url}?{self.next_querystring_attr}={next_querystring}&{querystring}'

    def get_next_options(self, request=None):
        """Returns the key/value pairs from the "next" querystring
        as a dictionary.
        """
        attrs = request.GET.dict().get(
            self.next_querystring_attr).split(',')[1:]
        return {k: request.GET.dict().get(k)
                for k in attrs if request.GET.dict().get(k)}
