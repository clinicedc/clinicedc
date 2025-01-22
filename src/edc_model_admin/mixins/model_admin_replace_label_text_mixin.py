from django.utils.html import format_html
from django.utils.safestring import mark_safe

NAME = 0
WIDGET = 1


class ModelAdminReplaceLabelTextMixin:
    @staticmethod
    def replace_label_text(form=None, old=None, new=None, skip_fields=None):
        skip_fields = skip_fields or []
        for fld in form.base_fields.items():
            if fld[NAME] not in skip_fields:
                label = str(fld[WIDGET].label)
                if old in label:
                    label = label.replace(old, new)
                    fld[WIDGET].label = format_html(
                        "{}",
                        mark_safe(label),  # nosec B703, B308
                    )
        return form
