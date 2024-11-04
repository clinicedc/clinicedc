from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import FileResponse
from django.utils.translation import gettext as _
from pylabels import Sheet, Specification

from .site_label_configs import LabelConfig, site_label_configs

if TYPE_CHECKING:
    from .models import LabelConfiguration


@admin.action(description="Test print sheet of labels")
def print_test_label_sheet_action(modeladmin, request, queryset: QuerySet[LabelConfiguration]):

    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            _("Select one and only one existing label specification"),
        )
    else:
        obj = queryset.first()
        label_config: LabelConfig = site_label_configs.get(obj.name)
        specs = Specification(**obj.label_specification.as_dict)
        sheet = Sheet(specs, label_config.drawing_func, border=obj.label_specification.border)

        try:
            label_cls = django_apps.get_model(label_config.label_cls)
        except (LookupError, AttributeError):
            label_cls = label_config.label_cls
        data = label_config.test_data_func()
        sheet.add_labels(
            [
                label_cls(**data)
                for i in range(
                    0, obj.label_specification.rows * obj.label_specification.columns
                )
            ]
        )
        buffer = sheet.save_to_buffer()
        return FileResponse(buffer, as_attachment=True, filename=f"test_print_{obj.name}.pdf")
    return None
