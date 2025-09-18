from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.http import FileResponse
from django.utils import timezone
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
        sheet = Sheet(
            specs, label_config.drawing_callable, border=obj.label_specification.border
        )

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


@admin.action(description="Print labels")
def print_label_sheet(modeladmin, request, queryset):
    if (
        queryset.model.objects.values("label_configuration__name")
        .filter(id__in=[obj.id for obj in queryset])
        .annotate(name=Count("label_configuration__name"))
        .count()
        > 1
    ):
        messages.add_message(
            request,
            messages.ERROR,
            _("Select items that have the same label configuration"),
        )
    else:
        label_data = [obj for obj in queryset]
        config: LabelConfiguration = queryset.first().label_configuration
        drawing_callable = site_label_configs.get(config.name).drawing_callable
        specs = Specification(**config.label_specification.as_dict)
        sheet = Sheet(specs, drawing_callable, border=config.label_specification.border)
        sheet.add_labels(label_data)
        buffer = sheet.save_to_buffer()
        now = timezone.now()
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"{config.name}_{now.strftime('%Y-%m-%d %H:%M')}.pdf",
        )
    return None
