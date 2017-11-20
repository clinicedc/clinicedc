from django.contrib.admin.widgets import AdminDateWidget
from django.forms.widgets import DateInput


class ModelAdminReadOnlyMixin:
    """
    A mixin that presents an admin form with the submit_row replaced
    with a Close button effectively making the form a read-only form.

        The Close button navigates to the "next" url from the
        GET/querystring.

        Subclass the change_form.html. Add

            {% block submit_buttons_bottom %}
            {% if edc_readonly %}
              <div class="submit_row"><input type="button"
              value="Close" class="default" name="_close"
              onclick="location.href='{{ edc_readonly_next }}';" />
              </div>
            {% else %}
              {% submit_row %}
            {% endif %}
            {% endblock %}

        to the admin url querystring add "next" and "edc_readonly=1"

    """

    def get_form(self, request, obj=None, **kwargs):
        form = super(ModelAdminReadOnlyMixin, self).get_form(
            request, obj, **kwargs)
        if request.GET.get('edc_readonly'):
            for form_field in form.base_fields.values():
                form_field.disabled = True
                try:
                    form_field.widget.can_add_related = False
                    form_field.widget.can_change_related = False
                    form_field.widget.can_delete_related = False
                except AttributeError:
                    pass
                if isinstance(form_field.widget, AdminDateWidget):
                    form_field.widget = DateInput()
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if request.GET.get('edc_readonly'):
            extra_context.update(
                {'edc_readonly': request.GET.get('edc_readonly')})
            extra_context.update(
                {'edc_readonly_next': request.GET.get(self.next_querystring_attr)})
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
