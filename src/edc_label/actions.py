from django.contrib import messages

from .label import Label


def print_labels_action(label_name, queryset, request, extra_context=None):
    label = Label(label_name)
    for obj in queryset:
        context = obj.extra_context or {}
        context.update(obj.label_context())
        label.print_label(context)
        if label.error_message:
            messages.add_message(request, messages.WARNING, label.error_message)
            break
        messages.add_message(request, messages.SUCCESS, label.message)
