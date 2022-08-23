from django.utils.html import format_html

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
                    fld[WIDGET].label = format_html(label)
        return form
