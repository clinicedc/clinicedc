import re
from copy import copy

from django.utils.html import format_html
from django.utils.safestring import mark_safe


class ModelAdminFormAutoNumberMixin:

    """Overrides get_form to insert question numbers and the DB
    field names.

    This is a mixin for `admin.ModelAdmin`

    Disable on the form by setting `form._meta.auto_number` to False.

    By default, auto_number it True.
    """

    skip_auto_numbering = []  # a list of fieldnames

    def auto_number(self, form):
        """Returns the form instance after inserting into the label
        question numbers and DB field names.
        """
        widget = 1
        start = getattr(form, "AUTO_NUMBER_START", 1)
        base_fields = {
            k: v for k, v in form.base_fields.items() if k not in self.skip_auto_numbering
        }
        for index, fld in enumerate(base_fields.items(), start=start):
            label = str(fld[widget].label)
            if not re.match(r"^\d+\.", label) and not re.match(r"\<a\ title\=\"", label):
                fld[widget].original_label = copy(label)
                fld[widget].label = format_html(
                    '<a title="{}">{}</a>. {}',
                    fld[0],
                    str(index),
                    mark_safe(label),  # nosec B308 B703
                )

        return form

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        form = self.auto_number(form)
        return form
