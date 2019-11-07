import re

from copy import copy
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
        WIDGET = 1
        start = getattr(form, "AUTO_NUMBER_START", 1)
        base_fields = {
            k: v
            for k, v in form.base_fields.items()
            if k not in self.skip_auto_numbering
        }
        for index, fld in enumerate(base_fields.items(), start=start):
            label = str(fld[WIDGET].label)
            if not re.match(r"^\d+\.", label) and not re.match(
                r"\<a\ title\=\"", label
            ):
                fld[WIDGET].original_label = copy(label)
                fld[WIDGET].label = mark_safe(
                    '<a title="{0}">{1}</a>. {2}'.format(fld[0], str(index), label)
                )
        return form

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form = self.auto_number(form)
        return form
