from io import StringIO

from django.contrib import messages
from django.http import FileResponse
from django_crypto_fields.utils import has_encrypted_fields


def export_to_csv(modeladmin, request, queryset):
    """This should be used carefully to ensure confidential
    data is not exported.
    """
    if queryset.count() == 0:
        messages.info(request, "Nothing to do.")
    elif has_encrypted_fields(queryset.model):
        messages.warning(request, "Unable to export. Report may contain confidential data")
    else:
        filename = f"{modeladmin.model._meta.label_lower.replace('.', '_')}.csv"
        buffer = StringIO()
        queryset.to_dataframe().to_csv(buffer, index=False)
        buffer.seek(0)
        response = FileResponse(buffer.read(), as_attachment=True, content_type="text/csv")
        response["Content-Disposition"] = f'filename="{filename}"'
        title = getattr(modeladmin, "change_list_title", modeladmin.model._meta.verbose_name)
        messages.success(request, f"Exported {title} to CSV. Check your browser's downloads")
        return response
    return None
