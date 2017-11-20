import re

from django.utils.safestring import mark_safe


class ModelAdminFormAutoNumberMixin:

    def auto_number(self, form):
        WIDGET = 1
        auto_number = True
        if 'auto_number' in dir(form._meta):
            auto_number = form._meta.auto_number
        if auto_number:
            for index, fld in enumerate(form.base_fields.items()):
                label = str(fld[WIDGET].label)
                if (not re.match(r'^\d+\.', label)
                        and not re.match(r'\<a\ title\=\"', label)):
                    fld[WIDGET].label = mark_safe(
                        '<a title="{0}">{1}</a>. {2}'.format(
                            fld[0], str(index + 1), label))
        return form

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form = self.auto_number(form)
        return form
